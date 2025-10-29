#!/usr/bin/env python3
"""
Polymarket Monolith Client
Complete solution for fetching, filtering, storing, and comparing Polymarket data
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import argparse

import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    polymarket_api_base_url: str = "https://gamma-api.polymarket.com"
    database_url: str = "postgresql://ranjanshahajishitole@localhost:5432/polymarket_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
logger = logging.getLogger(__name__)


class PolymarketClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.db_conn = None
        
        # Keywords for classification
        self.financial_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
            'stock', 'stocks', 'nasdaq', 's&p', 'dow', 'dow jones',
            'forex', 'fx', 'currency', 'usd', 'eur', 'gbp', 'jpy',
            'commodity', 'gold', 'silver', 'oil', 'crude', 'gas',
            'bond', 'bonds', 'treasury', 'fed', 'federal reserve',
            'inflation', 'gdp', 'unemployment', 'interest rate',
            'earnings', 'revenue', 'profit', 'dividend',
            'ipo', 'merger', 'acquisition', 'bankruptcy',
            'recession', 'bull market', 'bear market', 'volatility',
            'rate cut', 'rate increase', 'powell', 'jerome powell',
            'fed chair', 'fed governor', 'monetary policy',
            'yield', 'treasury yield', '10-year', '30-year'
        ]
        
        self.crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency'
        ]
        
        self.big_event_keywords = [
            'trump', 'donald trump', 'president', 'presidential', 'election', 'vote', 'voting',
            'white house', 'congress', 'senate', 'house', 'republican', 'democrat',
            'pardon', 'impeachment', 'inauguration', 'cabinet', 'supreme court',
            'fbi', 'cia', 'nsa', 'pentagon', 'state department',
            'war', 'conflict', 'peace', 'treaty', 'agreement', 'ceasefire',
            'ukraine', 'russia', 'putin', 'zelensky', 'nato',
            'israel', 'palestine', 'gaza', 'lebanon', 'hezbollah',
            'china', 'taiwan', 'north korea', 'iran', 'syria',
            'military', 'defense', 'weapon', 'missile', 'drone',
            'sanctions', 'embargo', 'invasion', 'occupation',
            'crisis', 'emergency', 'alert', 'warning', 'announcement',
            'shutdown', 'government shutdown', 'debt ceiling',
            'trade war', 'tariff', 'china trade', 'us-china'
        ]
        
        self.exclude_keywords = [
            'football game', 'soccer match', 'basketball game', 'baseball game', 'tennis match',
            'golf tournament', 'hockey game', 'cricket match', 'rugby match', 'volleyball game',
            'badminton tournament', 'table tennis', 'swimming competition', 'running race', 'cycling race',
            'boxing match', 'mma fight', 'ufc fight', 'wrestling match', 'fencing competition',
            'olympics', 'world cup', 'championship game', 'tournament final',
            ' vs ', 'team sport', 'player stats',
            'fc', 'afc', 'united fc', 'arsenal fc', 'chelsea fc',
            'liverpool fc', 'manchester united', 'real madrid', 'barcelona fc',
            'nba game', 'nfl game', 'mlb game', 'nhl game', 'fifa world cup', 'uefa',
            'f1 drivers', 'poker championship', 'heads-up poker', 'world series',
            'movie release', 'film premiere', 'cinema screening', 'hollywood movie', 'oscar award',
            'emmy award', 'grammy award', 'golden globe', 'award ceremony', 'awards show',
            'movie actor', 'movie actress', 'film director', 'movie producer', 'movie studio',
            'netflix series', 'disney movie', 'marvel movie', 'dc movie', 'superhero movie',
            'avatar movie', 'star wars movie', 'harry potter movie', 'batman movie', 'superman movie',
            'opening weekend', 'box office', 'movie grossing', 'movie sequel',
            'celebrity gossip', 'famous person', 'social media influencer', 'instagram post',
            'twitter post', 'tiktok video', 'youtube video', 'music streaming',
            'music song', 'music album', 'music concert', 'music tour', 'music band',
            'taylor swift concert', 'beyonce concert', 'kanye concert', 'drake concert', 'bts concert',
            'artificial intelligence', 'chatgpt', 'openai', 'ai chatbot',
            'tesla car', 'spacex rocket', 'elon musk tweet', 'meta platform', 'facebook post',
            'google search', 'apple iphone', 'microsoft office', 'amazon delivery', 'netflix show',
            'video game', 'esports tournament', 'twitch stream', 'gaming stream',
            'netherlands', 'dutch', 'romania', 'bucharest', 'argentina', 'deputies election',
            'chile', 'chilean', 'megaeth', 'mega eth', 'public sale', 'total commitments'
        ]
    
    async def close(self):
        await self.client.aclose()
        if self.db_conn:
            self.db_conn.close()
    
    def get_db_connection(self):
        if not self.db_conn or self.db_conn.closed:
            self.db_conn = psycopg2.connect(settings.database_url)
        return self.db_conn
    
    def _is_financial(self, data: Dict[str, Any]) -> bool:
        title = (data.get('title') or '').lower()
        description = (data.get('description') or '').lower()
        category = (data.get('category') or '').lower()
        text_to_check = f"{title} {description} {category}"
        return any(keyword in text_to_check for keyword in self.financial_keywords)

    def _is_crypto(self, data: Dict[str, Any]) -> bool:
        title = (data.get('title') or '').lower()
        description = (data.get('description') or '').lower()
        category = (data.get('category') or '').lower()
        text_to_check = f"{title} {description} {category}"
        return any(keyword in text_to_check for keyword in self.crypto_keywords)

    def _is_big_event(self, data: Dict[str, Any]) -> bool:
        title = (data.get('title') or '').lower()
        description = (data.get('description') or '').lower()
        category = (data.get('category') or '').lower()
        text_to_check = f"{title} {description} {category}"
        return any(keyword in text_to_check for keyword in self.big_event_keywords)
    
    def _is_excluded(self, data: Dict[str, Any]) -> bool:
        title = (data.get('title') or '').lower()
        description = (data.get('description') or '').lower()
        category = (data.get('category') or '').lower()
        text_to_check = f"{title} {description} {category}"
        return any(keyword in text_to_check for keyword in self.exclude_keywords)
    
    def _is_us_crypto_fed_only(self, data: Dict[str, Any]) -> bool:
        title = (data.get('title') or '').lower()
        description = (data.get('description') or '').lower()
        category = (data.get('category') or '').lower()
        text_to_check = f"{title} {description} {category}"
        
        us_keywords = [
            'trump', 'donald trump', 'presidential nominee', 'presidential election winner',
            'presidential election', 'us presidential', 'us election', 'american presidential',
            'white house', 'us congress', 'us senate', 'us house', 'republican presidential',
            'democratic presidential', 'us republican', 'us democrat',
            'government shutdown', 'debt ceiling', ' us ', ' usa ', 'united states',
            'nyc', 'new york city', 'us recession',
            'us x ', 'us-', 'president of the united states', 'us forces', 'us military',
            'us recession', 'us economy', 'us inflation', 'us unemployment'
        ]
        
        fed_keywords = [
            'fed', 'federal reserve', 'fomc', 'powell', 'jerome powell',
            'fed chair', 'fed governor', 'monetary policy',
            'rate cut', 'rate increase', 'interest rate',
            'fed decision', 'fomc meeting', 'fed meeting'
        ]
        
        crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency'
        ]
        
        war_keywords = [
            'ukraine', 'russia', 'putin', 'zelensky', 'nato',
            'israel', 'palestine', 'gaza', 'lebanon', 'hezbollah',
            'china', 'taiwan', 'north korea', 'iran', 'syria',
            'military', 'defense', 'weapon', 'missile', 'drone',
            'sanctions', 'embargo', 'invasion', 'occupation',
            'war', 'conflict', 'peace', 'treaty', 'agreement', 'ceasefire'
        ]
        
        is_us = any(keyword in text_to_check for keyword in us_keywords)
        is_fed = any(keyword in text_to_check for keyword in fed_keywords)
        is_crypto = any(keyword in text_to_check for keyword in crypto_keywords)
        is_war = any(keyword in text_to_check for keyword in war_keywords)
        
        return is_us or is_fed or is_crypto or is_war
    
    async def fetch_events(self, limit: int = 500) -> List[Dict[str, Any]]:
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
            logger.error(f"Error fetching events: {e}")
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
    
    def classify_events(self, events_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        classified = {
            'financial': [],
            'crypto': [],
            'big_events': [],
            'high_volume': [],
            'all': []
        }
        
        for event in events_data:
            if self._is_excluded(event):
                continue
                    
            if not event.get('active', True):
                continue
                    
            if not event.get('volume') or event['volume'] < 5000000:
                continue
            
            if not self._is_us_crypto_fed_only(event):
                continue
                    
            classified['all'].append(event)
            
            event['is_financial'] = self._is_financial(event)
            event['is_crypto'] = self._is_crypto(event)
            event['is_big_event'] = self._is_big_event(event)
            event['is_excluded'] = False
            
            if event['is_financial']:
                classified['financial'].append(event)
            
            if event['is_crypto']:
                classified['crypto'].append(event)
            
            if event['is_big_event']:
                classified['big_events'].append(event)
            
            classified['high_volume'].append(event)
        
        return classified

    def clean_event_data(self, event: Dict[str, Any]) -> Dict[str, Any]:
        essential_event_fields = {
            'id', 'title', 'description', 'endDate', 'active',
            'liquidity', 'volume', 'is_financial', 'is_crypto', 'is_big_event', 'is_excluded',
            'volume24hr', 'liquidityClob', 'resolutionSource'
        }
        
        cleaned_event = {k: v for k, v in event.items() if k in essential_event_fields}
        
        if 'markets' in event and event['markets']:
            cleaned_markets = []
            total_volume = 0
            total_liquidity = 0
            
            for market in event['markets']:
                cleaned_market = self.clean_market_data(market)
                if cleaned_market is None:
                    continue
                        
                cleaned_markets.append(cleaned_market)
                
                if cleaned_market.get('volume'):
                    total_volume += float(cleaned_market['volume'])
                if cleaned_market.get('liquidity'):
                    total_liquidity += float(cleaned_market['liquidity'])
            
            cleaned_event['markets'] = cleaned_markets
            
            if total_volume > 0:
                cleaned_event['volume'] = total_volume
            if total_liquidity > 0:
                cleaned_event['liquidity'] = total_liquidity
        
        return cleaned_event
    
    def clean_market_data(self, market: Dict[str, Any]) -> Dict[str, Any]:
        volume24hr = market.get('volume24hr', 0)
        try:
            volume24hr = float(volume24hr) if volume24hr else 0
        except (ValueError, TypeError):
            volume24hr = 0
        
        if volume24hr < 5000000:
            return None
        
        market_volume = market.get('volume', 0)
        try:
            market_volume = float(market_volume) if market_volume else 0
        except (ValueError, TypeError):
            market_volume = 0
        
        if market_volume < 100:
            return None
        
        essential_market_fields = {
            'id', 'question', 'endDate', 'liquidity', 'volume',
            'outcomes', 'outcomePrices', 'active', 'description',
            'volume24hr'
        }
        
        cleaned_market = {k: v for k, v in market.items() if k in essential_market_fields}
        return cleaned_market

    def save_to_json(self, data, filename: str):
        try:
            if isinstance(data, list):
                cleaned_data = [self.clean_event_data(event) for event in data]
            else:
                cleaned_data = data.copy()
                for category in ['financial_events', 'crypto_events', 'politics_war_events', 'high_volume_events', 'all_events']:
                    if category in cleaned_data:
                        cleaned_data[category] = [self.clean_event_data(event) for event in cleaned_data[category]]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, default=str, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to {filename}: {e}")
    
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
            'compared_at': datetime.now(timezone.utc).isoformat()
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
            'compared_at': datetime.now(timezone.utc).isoformat()
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
    
    def create_tables(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id BIGINT PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                end_date TIMESTAMP WITH TIME ZONE,
                active BOOLEAN NOT NULL DEFAULT true,
                liquidity DECIMAL(20,2),
                volume DECIMAL(20,2),
                volume24hr DECIMAL(20,2),
                liquidity_clob DECIMAL(20,2),
                resolution_source TEXT,
                is_financial BOOLEAN NOT NULL DEFAULT false,
                is_crypto BOOLEAN NOT NULL DEFAULT false,
                is_big_event BOOLEAN NOT NULL DEFAULT false,
                is_excluded BOOLEAN NOT NULL DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS markets (
                id BIGINT PRIMARY KEY,
                event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                question TEXT NOT NULL,
                end_date TIMESTAMP WITH TIME ZONE,
                liquidity DECIMAL(20,2),
                volume DECIMAL(20,2),
                volume24hr DECIMAL(20,2),
                outcomes JSONB,
                outcome_prices JSONB,
                active BOOLEAN NOT NULL DEFAULT true,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_differences (
                id SERIAL PRIMARY KEY,
                event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                differences_data JSONB NOT NULL,
                compared_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(event_id, compared_at)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_differences (
                id SERIAL PRIMARY KEY,
                market_id BIGINT NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
                event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                differences_data JSONB NOT NULL,
                compared_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(market_id, compared_at)
            );
        """)
        
        conn.commit()
        cursor.close()
        logger.info("Database tables created successfully")
    
    async def fetch_and_store(self):
        logger.info("Fetching events from API...")
        events_data = await self.fetch_events(limit=500)
        logger.info(f"Fetched {len(events_data)} events")
        
        if not events_data:
            logger.warning("No events found")
            return

        classified = self.classify_events(events_data)
        
        all_data = {
            'summary': {
                'total_events': len(classified['all']),
                'financial_events': len(classified['financial']),
                'crypto_events': len(classified['crypto']),
                'politics_war_events': len(classified['big_events']),
                'high_volume_events': len(classified['high_volume']),
                'total_volume': sum(event.get('volume', 0) for event in classified['all'] if event.get('volume')),
                'total_liquidity': sum(event.get('liquidity', 0) for event in classified['all'] if event.get('liquidity'))
            },
            'financial_events': classified['financial'],
            'crypto_events': classified['crypto'],
            'politics_war_events': classified['big_events'],
            'high_volume_events': classified['high_volume'],
            'all_events': classified['all']
        }
        
        self.save_to_json(all_data, 'polymarket_data.json')
        logger.info(f"Processed {len(classified['all'])} events")
    
    async def compare_data(self):
        logger.info("Fetching stored events from database...")
        stored_events = self.fetch_stored_events()
        logger.info(f"Found {len(stored_events)} stored events")
        
        logger.info("Fetching fresh events from API...")
        fresh_events = await self.fetch_events(limit=500)
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
    parser = argparse.ArgumentParser(description='Polymarket Monolith Client')
    parser.add_argument('command', choices=['fetch', 'compare', 'setup'], 
                       help='Command to run: fetch (get data), compare (compare data), setup (create tables)')
    parser.add_argument('--limit', type=int, default=500, help='Number of events to fetch')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    client = PolymarketClient()
    
    try:
        if args.command == 'setup':
            client.create_tables()
        elif args.command == 'fetch':
            await client.fetch_and_store()
        elif args.command == 'compare':
            await client.compare_data()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
