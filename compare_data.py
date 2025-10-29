import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import httpx
import psycopg2
from psycopg2.extras import RealDictCursor

from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PolymarketComparator:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.db_conn = None
    
    async def close(self):
        await self.client.aclose()
        if self.db_conn:
            self.db_conn.close()
    
    def get_db_connection(self):
        if not self.db_conn or self.db_conn.closed:
            self.db_conn = psycopg2.connect(settings.database_url)
        return self.db_conn
    
    def fetch_stored_events(self) -> List[Dict[str, Any]]:
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT e.*, 
                   json_agg(
                       json_build_object(
                           'id', m.id,
                           'question', m.question,
                           'volume', m.volume,
                           'volume24hr', m.volume24hr,
                           'liquidity', m.liquidity,
                           'outcomes', m.outcomes,
                           'outcome_prices', m.outcome_prices,
                           'active', m.active
                       )
                   ) FILTER (WHERE m.id IS NOT NULL) as markets
            FROM events e
            LEFT JOIN markets m ON e.id = m.event_id
            WHERE e.active = true
            GROUP BY e.id
            ORDER BY e.volume DESC
        """)
        
        events = []
        for row in cursor.fetchall():
            event_dict = dict(row)
            if event_dict['markets']:
                event_dict['markets'] = [dict(m) for m in event_dict['markets']]
            else:
                event_dict['markets'] = []
            events.append(event_dict)
        
        cursor.close()
        return events
    
    async def fetch_fresh_events(self, limit: int = 500) -> List[Dict[str, Any]]:
        try:
            response = await self.client.get(
                f"{settings.polymarket_api_base_url}/events",
                params={
                    'limit': limit,
                    'closed': False,
                    'order': 'volume',
                    'ascending': False
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching fresh events: {e}")
            return []
    
    async def fetch_market_details(self, market_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = await self.client.get(
                f"{settings.polymarket_api_base_url}/markets/{market_id}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.debug(f"Error fetching market {market_id} details: {e}")
            return None
    
    def parse_outcome_prices(self, prices_data: Any) -> Dict[str, float]:
        if isinstance(prices_data, dict):
            return {k: float(v) for k, v in prices_data.items()}
        elif isinstance(prices_data, str):
            try:
                parsed = json.loads(prices_data)
                if isinstance(parsed, list):
                    return {str(i): float(p) for i, p in enumerate(parsed)}
                return {k: float(v) for k, v in parsed.items()}
            except:
                return {}
        elif isinstance(prices_data, list):
            return {str(i): float(p) for i, p in enumerate(prices_data)}
        return {}
    
    def calculate_price_difference(self, old_prices: Dict[str, float], new_prices: Dict[str, float]) -> Dict[str, float]:
        differences = {}
        all_keys = set(old_prices.keys()) | set(new_prices.keys())
        
        for key in all_keys:
            old_val = old_prices.get(key, 0.0)
            new_val = new_prices.get(key, 0.0)
            diff = new_val - old_val
            if abs(diff) > 0.0001:
                differences[key] = diff
        
        return differences
    
    async def compare_market(self, stored_market: Dict[str, Any], fresh_market: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        differences = {}
        has_changes = False
        
        market_id = stored_market.get('id')
        if str(market_id) != str(fresh_market.get('id')):
            return None
        
        stored_volume = float(stored_market.get('volume', 0) or 0)
        fresh_volume = float(fresh_market.get('volume', 0) or 0)
        volume_diff = fresh_volume - stored_volume
        if abs(volume_diff) >= 100:
            differences['volume'] = {
                'old': stored_volume,
                'new': fresh_volume,
                'difference': volume_diff,
                'percent_change': (volume_diff / stored_volume * 100) if stored_volume > 0 else 0
            }
            has_changes = True
        
        stored_volume24hr = float(stored_market.get('volume24hr', 0) or 0)
        fresh_volume24hr = float(fresh_market.get('volume24hr', 0) or 0)
        volume24hr_diff = fresh_volume24hr - stored_volume24hr
        if abs(volume24hr_diff) >= 100:
            differences['volume24hr'] = {
                'old': stored_volume24hr,
                'new': fresh_volume24hr,
                'difference': volume24hr_diff,
                'percent_change': (volume24hr_diff / stored_volume24hr * 100) if stored_volume24hr > 0 else 0
            }
            has_changes = True
        
        stored_liquidity = float(stored_market.get('liquidity', 0) or 0)
        fresh_liquidity = float(fresh_market.get('liquidity', 0) or 0)
        liquidity_diff = fresh_liquidity - stored_liquidity
        if abs(liquidity_diff) >= 100:
            differences['liquidity'] = {
                'old': stored_liquidity,
                'new': fresh_liquidity,
                'difference': liquidity_diff,
                'percent_change': (liquidity_diff / stored_liquidity * 100) if stored_liquidity > 0 else 0
            }
            has_changes = True
        
        stored_prices = self.parse_outcome_prices(stored_market.get('outcome_prices'))
        fresh_prices = self.parse_outcome_prices(fresh_market.get('outcomePrices'))
        price_diffs = self.calculate_price_difference(stored_prices, fresh_prices)
        if price_diffs:
            differences['prices'] = {
                'old': stored_prices,
                'new': fresh_prices,
                'differences': price_diffs
            }
            has_changes = True
        
        market_details = await self.fetch_market_details(str(market_id))
        if market_details:
            stored_oi = stored_market.get('open_interest')
            fresh_oi = market_details.get('openInterest') or market_details.get('open_interest')
            if stored_oi is not None and fresh_oi is not None:
                stored_oi_val = float(stored_oi) if stored_oi else 0
                fresh_oi_val = float(fresh_oi) if fresh_oi else 0
                oi_diff = fresh_oi_val - stored_oi_val
                if abs(oi_diff) >= 100:
                    differences['open_interest'] = {
                        'old': stored_oi_val,
                        'new': fresh_oi_val,
                        'difference': oi_diff,
                        'percent_change': (oi_diff / stored_oi_val * 100) if stored_oi_val > 0 else 0
                    }
                    has_changes = True
            
            stored_best_bid = stored_market.get('best_bid')
            fresh_best_bid = market_details.get('bestBid') or market_details.get('best_bid')
            if stored_best_bid is not None and fresh_best_bid is not None:
                stored_bid_val = float(stored_best_bid) if stored_best_bid else 0
                fresh_bid_val = float(fresh_best_bid) if fresh_best_bid else 0
                bid_diff = fresh_bid_val - stored_bid_val
                if abs(bid_diff) > 0.0001:
                    differences['best_bid'] = {
                        'old': stored_bid_val,
                        'new': fresh_bid_val,
                        'difference': bid_diff
                    }
                    has_changes = True
            
            stored_best_ask = stored_market.get('best_ask')
            fresh_best_ask = market_details.get('bestAsk') or market_details.get('best_ask')
            if stored_best_ask is not None and fresh_best_ask is not None:
                stored_ask_val = float(stored_best_ask) if stored_best_ask else 0
                fresh_ask_val = float(fresh_best_ask) if fresh_best_ask else 0
                ask_diff = fresh_ask_val - stored_ask_val
                if abs(ask_diff) > 0.0001:
                    differences['best_ask'] = {
                        'old': stored_ask_val,
                        'new': fresh_ask_val,
                        'difference': ask_diff
                    }
                    has_changes = True
        
        if not has_changes:
            return None
        
        return {
            'market_id': market_id,
            'event_id': stored_market.get('event_id'),
            'differences': differences,
            'compared_at': datetime.utcnow().isoformat()
        }
    
    async def compare_event(self, stored_event: Dict[str, Any], fresh_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        differences = {}
        has_changes = False
        
        event_id = stored_event.get('id')
        if str(event_id) != str(fresh_event.get('id')):
            return None
        
        stored_volume = float(stored_event.get('volume', 0) or 0)
        fresh_volume = float(fresh_event.get('volume', 0) or 0)
        volume_diff = fresh_volume - stored_volume
        if abs(volume_diff) >= 1000:
            differences['volume'] = {
                'old': stored_volume,
                'new': fresh_volume,
                'difference': volume_diff,
                'percent_change': (volume_diff / stored_volume * 100) if stored_volume > 0 else 0
            }
            has_changes = True
        
        stored_volume24hr = float(stored_event.get('volume24hr', 0) or 0)
        fresh_volume24hr = float(fresh_event.get('volume24hr', 0) or 0)
        volume24hr_diff = fresh_volume24hr - stored_volume24hr
        if abs(volume24hr_diff) >= 1000:
            differences['volume24hr'] = {
                'old': stored_volume24hr,
                'new': fresh_volume24hr,
                'difference': volume24hr_diff,
                'percent_change': (volume24hr_diff / stored_volume24hr * 100) if stored_volume24hr > 0 else 0
            }
            has_changes = True
        
        stored_liquidity = float(stored_event.get('liquidity', 0) or 0)
        fresh_liquidity = float(fresh_event.get('liquidity', 0) or 0)
        liquidity_diff = fresh_liquidity - stored_liquidity
        if abs(liquidity_diff) >= 1000:
            differences['liquidity'] = {
                'old': stored_liquidity,
                'new': fresh_liquidity,
                'difference': liquidity_diff,
                'percent_change': (liquidity_diff / stored_liquidity * 100) if stored_liquidity > 0 else 0
            }
            has_changes = True
        
        stored_liquidity_clob = float(stored_event.get('liquidity_clob', 0) or 0)
        fresh_liquidity_clob = float(fresh_event.get('liquidityClob', 0) or 0)
        liquidity_clob_diff = fresh_liquidity_clob - stored_liquidity_clob
        if abs(liquidity_clob_diff) >= 1000:
            differences['liquidity_clob'] = {
                'old': stored_liquidity_clob,
                'new': fresh_liquidity_clob,
                'difference': liquidity_clob_diff,
                'percent_change': (liquidity_clob_diff / stored_liquidity_clob * 100) if stored_liquidity_clob > 0 else 0
            }
            has_changes = True
        
        market_differences = []
        stored_markets = {str(m.get('id')): m for m in stored_event.get('markets', [])}
        fresh_markets = {str(m.get('id')): m for m in fresh_event.get('markets', [])}
        
        for market_id, stored_market in stored_markets.items():
            if market_id in fresh_markets:
                market_diff = await self.compare_market(stored_market, fresh_markets[market_id])
                if market_diff:
                    market_differences.append(market_diff)
        
        if market_differences:
            differences['markets'] = market_differences
            has_changes = True
        
        if not has_changes:
            return None
        
        return {
            'event_id': event_id,
            'differences': differences,
            'compared_at': datetime.utcnow().isoformat()
        }
    
    def store_differences(self, event_differences: List[Dict[str, Any]]):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        for diff in event_differences:
            event_id = diff['event_id']
            differences_json = json.dumps(diff['differences'])
            compared_at = datetime.fromisoformat(diff['compared_at'].replace('Z', '+00:00'))
            
            cursor.execute("""
                INSERT INTO data_differences (
                    event_id, differences_data, compared_at
                ) VALUES (%s, %s, %s)
                ON CONFLICT (event_id, compared_at) DO UPDATE SET
                    differences_data = EXCLUDED.differences_data,
                    updated_at = CURRENT_TIMESTAMP
            """, (event_id, differences_json, compared_at))
            
            if 'markets' in diff['differences']:
                for market_diff in diff['differences']['markets']:
                    market_id = market_diff['market_id']
                    market_diff_json = json.dumps(market_diff['differences'])
                    
                    cursor.execute("""
                        INSERT INTO market_differences (
                            market_id, event_id, differences_data, compared_at
                        ) VALUES (%s, %s, %s, %s)
                        ON CONFLICT (market_id, compared_at) DO UPDATE SET
                            differences_data = EXCLUDED.differences_data,
                            updated_at = CURRENT_TIMESTAMP
                    """, (market_id, event_id, market_diff_json, compared_at))
        
        conn.commit()
        cursor.close()
    
    async def run_comparison(self):
        logger.info("Fetching stored events from database...")
        stored_events = self.fetch_stored_events()
        logger.info(f"Found {len(stored_events)} stored events")
        
        logger.info("Fetching fresh events from API...")
        fresh_events = await self.fetch_fresh_events(limit=500)
        logger.info(f"Fetched {len(fresh_events)} fresh events")
        
        fresh_events_dict = {str(e.get('id')): e for e in fresh_events}
        
        event_differences = []
        compared_count = 0
        
        for stored_event in stored_events:
            event_id = str(stored_event.get('id'))
            if event_id in fresh_events_dict:
                compared_count += 1
                diff = await self.compare_event(stored_event, fresh_events_dict[event_id])
                if diff:
                    event_differences.append(diff)
        
        logger.info(f"Compared {compared_count} events, found {len(event_differences)} with changes")
        
        if event_differences:
            logger.info("Storing differences in database...")
            self.store_differences(event_differences)
            logger.info(f"Stored {len(event_differences)} event differences")
        else:
            logger.info("No differences found")


async def main():
    comparator = PolymarketComparator()
    try:
        await comparator.run_comparison()
    except Exception as e:
        logger.error(f"Error during comparison: {e}")
    finally:
        await comparator.close()


if __name__ == "__main__":
    asyncio.run(main())
