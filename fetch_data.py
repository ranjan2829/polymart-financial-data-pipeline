import asyncio
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

import httpx

from config import settings

logger = logging.getLogger(__name__)


class PolymarketSync:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Keywords for classification - STRICT FINANCIAL ONLY
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
        
        # Keywords for US/Trump/War events ONLY
        self.big_event_keywords = [
            # US Politics
            'trump', 'donald trump', 'president', 'presidential', 'election', 'vote', 'voting',
            'white house', 'congress', 'senate', 'house', 'republican', 'democrat',
            'pardon', 'impeachment', 'inauguration', 'cabinet', 'supreme court',
            'fbi', 'cia', 'nsa', 'pentagon', 'state department',
            
            # War/Conflict
            'war', 'conflict', 'peace', 'treaty', 'agreement', 'ceasefire',
            'ukraine', 'russia', 'putin', 'zelensky', 'nato',
            'israel', 'palestine', 'gaza', 'lebanon', 'hezbollah',
            'china', 'taiwan', 'north korea', 'iran', 'syria',
            'military', 'defense', 'weapon', 'missile', 'drone',
            'sanctions', 'embargo', 'invasion', 'occupation',
            
            # Crisis/Geopolitical
            'crisis', 'emergency', 'alert', 'warning', 'announcement',
            'shutdown', 'government shutdown', 'debt ceiling',
            'trade war', 'tariff', 'china trade', 'us-china'
        ]
        
        # Keywords to exclude (non-financial/political) - more specific
        self.exclude_keywords = [
                # Sports - specific terms only
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
                
                # Entertainment/Movies - specific terms only
                'movie release', 'film premiere', 'cinema screening', 'hollywood movie', 'oscar award',
                'emmy award', 'grammy award', 'golden globe', 'award ceremony', 'awards show',
                'movie actor', 'movie actress', 'film director', 'movie producer', 'movie studio',
                'netflix series', 'disney movie', 'marvel movie', 'dc movie', 'superhero movie',
                'avatar movie', 'star wars movie', 'harry potter movie', 'batman movie', 'superman movie',
                'opening weekend', 'box office', 'movie grossing', 'movie sequel',
                
                # Celebrity/Culture - specific terms only
                'celebrity gossip', 'famous person', 'social media influencer', 'instagram post',
                'twitter post', 'tiktok video', 'youtube video', 'music streaming',
                'music song', 'music album', 'music concert', 'music tour', 'music band',
                'taylor swift concert', 'beyonce concert', 'kanye concert', 'drake concert', 'bts concert',
                
                # Tech/Non-Financial - specific terms only
                'artificial intelligence', 'chatgpt', 'openai', 'ai chatbot',
                'tesla car', 'spacex rocket', 'elon musk tweet', 'meta platform', 'facebook post',
                'google search', 'apple iphone', 'microsoft office', 'amazon delivery', 'netflix show',
                'video game', 'esports tournament', 'twitch stream', 'gaming stream',
                
                # Non-US countries/regions - exclude these
                'netherlands', 'dutch', 'romania', 'bucharest', 'argentina', 'deputies election',
                'chile', 'chilean', 'megaeth', 'mega eth', 'public sale', 'total commitments'
            ]
    
    async def close(self):
        await self.client.aclose()
    
    def _is_financial(self, data: Dict[str, Any]) -> bool:
        """Check if data is financial related"""
        title = (data.get('title') or '').lower()
        description = (data.get('description') or '').lower()
        category = (data.get('category') or '').lower()
        text_to_check = f"{title} {description} {category}"
        return any(keyword in text_to_check for keyword in self.financial_keywords)
    
    def _is_crypto(self, data: Dict[str, Any]) -> bool:
        """Check if data is crypto related"""
        title = (data.get('title') or '').lower()
        description = (data.get('description') or '').lower()
        category = (data.get('category') or '').lower()
        text_to_check = f"{title} {description} {category}"
        return any(keyword in text_to_check for keyword in self.crypto_keywords)
    
    def _is_big_event(self, data: Dict[str, Any]) -> bool:
        """Check if data is a big event (US politics/war only)"""
        title = (data.get('title') or '').lower()
        description = (data.get('description') or '').lower()
        category = (data.get('category') or '').lower()
        text_to_check = f"{title} {description} {category}"
        
        return any(keyword in text_to_check for keyword in self.big_event_keywords)
    
    def _is_excluded(self, data: Dict[str, Any]) -> bool:
        """Check if data should be excluded (sports, movies, entertainment, etc.)"""
        title = (data.get('title') or '').lower()
        description = (data.get('description') or '').lower()
        category = (data.get('category') or '').lower()
        text_to_check = f"{title} {description} {category}"
        return any(keyword in text_to_check for keyword in self.exclude_keywords)
    
    def _is_us_crypto_fed_only(self, data: Dict[str, Any]) -> bool:
        """Check if event is US-related, crypto-related, or Fed-related"""
        title = (data.get('title') or '').lower()
        description = (data.get('description') or '').lower()
        category = (data.get('category') or '').lower()
        text_to_check = f"{title} {description} {category}"
        
        # US-related keywords - must be explicitly US-related
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
        
        # Fed-related keywords
        fed_keywords = [
            'fed', 'federal reserve', 'fomc', 'powell', 'jerome powell',
            'fed chair', 'fed governor', 'monetary policy',
            'rate cut', 'rate increase', 'interest rate',
            'fed decision', 'fomc meeting', 'fed meeting'
        ]
        
        # Crypto keywords - only major cryptos, no specific projects
        crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency'
        ]
        
        # War/Conflict keywords - must be US-related or major global conflicts
        war_keywords = [
            'ukraine', 'russia', 'putin', 'zelensky', 'nato',
            'israel', 'palestine', 'gaza', 'lebanon', 'hezbollah',
            'china', 'taiwan', 'north korea', 'iran', 'syria',
            'military', 'defense', 'weapon', 'missile', 'drone',
            'sanctions', 'embargo', 'invasion', 'occupation',
            'war', 'conflict', 'peace', 'treaty', 'agreement', 'ceasefire'
        ]
        
        # Check if event matches any of the four categories
        is_us = any(keyword in text_to_check for keyword in us_keywords)
        is_fed = any(keyword in text_to_check for keyword in fed_keywords)
        is_crypto = any(keyword in text_to_check for keyword in crypto_keywords)
        is_war = any(keyword in text_to_check for keyword in war_keywords)
        
        return is_us or is_fed or is_crypto or is_war
    
    async def fetch_events(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Fetch events from API"""
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
    
    def classify_events(self, events_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Classify events into categories (FINANCIAL/TRUMP/WAR ONLY)"""
        classified = {
            'financial': [],
            'crypto': [],
            'big_events': [],
            'high_volume': [],
            'all': []
        }
        
        for event in events_data:
            # Skip excluded events (sports, movies, entertainment, etc.)
            if self._is_excluded(event):
                continue
                
            # Skip inactive events
            if not event.get('active', True):
                continue
                
            # Skip events with volume less than $5 million
            if not event.get('volume') or event['volume'] < 5000000:
                continue
            
            # FILTER: Only include US, crypto, or Fed-related events
            if not self._is_us_crypto_fed_only(event):
                continue
            
            # Add to all events (filtered only)
            classified['all'].append(event)
            
            # Add classification flags
            event['is_financial'] = self._is_financial(event)
            event['is_crypto'] = self._is_crypto(event)
            event['is_big_event'] = self._is_big_event(event)
            event['is_excluded'] = False  # Always false since we filter out excluded
            
            # Categorize
            if event['is_financial']:
                classified['financial'].append(event)
            
            if event['is_crypto']:
                classified['crypto'].append(event)
            
            if event['is_big_event']:
                classified['big_events'].append(event)
            
            # High volume events (volume >= 500,000) - now all events are >= 5M
            classified['high_volume'].append(event)
        
        return classified
    
    
    def clean_event_data(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Clean event data by removing unnecessary fields and aggregating volume/liquidity"""
        # Essential event fields to keep
        essential_event_fields = {
            'id', 'title', 'description', 'endDate', 'active',
            'liquidity', 'volume', 'is_financial', 'is_crypto', 'is_big_event', 'is_excluded',
            'volume24hr', 'liquidityClob', 'resolutionSource'
        }
        
        # Clean event data
        cleaned_event = {k: v for k, v in event.items() if k in essential_event_fields}
        
        # Clean markets if they exist and aggregate volume/liquidity
        if 'markets' in event and event['markets']:
            cleaned_markets = []
            total_volume = 0
            total_liquidity = 0
            
            for market in event['markets']:
                cleaned_market = self.clean_market_data(market)
                if cleaned_market is None:  # Skip markets with zero/low volume
                    continue
                    
                cleaned_markets.append(cleaned_market)
                
                # Aggregate volume and liquidity from markets
                if cleaned_market.get('volume'):
                    total_volume += float(cleaned_market['volume'])
                if cleaned_market.get('liquidity'):
                    total_liquidity += float(cleaned_market['liquidity'])
                
            cleaned_event['markets'] = cleaned_markets
            
            # Update event volume and liquidity with aggregated values
            if total_volume > 0:
                cleaned_event['volume'] = total_volume
            if total_liquidity > 0:
                cleaned_event['liquidity'] = total_liquidity
        
        return cleaned_event
    
    def clean_market_data(self, market: Dict[str, Any]) -> Dict[str, Any]:
        """Clean market data by removing unnecessary fields and filtering out zero/low volume markets"""
        # Filter out markets with volume24hr < $5 million
        volume24hr = market.get('volume24hr', 0)
        try:
            volume24hr = float(volume24hr) if volume24hr else 0
        except (ValueError, TypeError):
            volume24hr = 0
        
        # Skip markets with volume24hr < $5 million
        if volume24hr < 5000000:
            return None
        
        # Filter out markets with volume 0 or very low volume (< $100)
        market_volume = market.get('volume', 0)
        try:
            market_volume = float(market_volume) if market_volume else 0
        except (ValueError, TypeError):
            market_volume = 0
        
        # Skip markets with volume < $100
        if market_volume < 100:
            return None
        
        # Essential market fields to keep
        essential_market_fields = {
            'id', 'question', 'endDate', 'liquidity', 'volume',
            'outcomes', 'outcomePrices', 'active', 'description',
            'volume24hr'
        }
        
        # Clean market data
        cleaned_market = {k: v for k, v in market.items() if k in essential_market_fields}
        
        return cleaned_market

    def save_to_json(self, data, filename: str):
        """Save cleaned data to JSON file"""
        try:
            # If it's a list of events, clean them
            if isinstance(data, list):
                cleaned_data = [self.clean_event_data(event) for event in data]
            else:
                # If it's a dict with multiple categories, clean each category
                cleaned_data = data.copy()
                for category in ['financial_events', 'crypto_events', 'politics_war_events', 'high_volume_events', 'all_events']:
                    if category in cleaned_data:
                        cleaned_data[category] = [self.clean_event_data(event) for event in cleaned_data[category]]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, default=str, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to {filename}: {e}")
    


async def main():
    """Main function"""
    
    sync = PolymarketSync()
    
    try:
        events_data = await sync.fetch_events(limit=500)
        logger.info(f"Fetched {len(events_data)} events")
        
        if not events_data:
            logger.warning("No events found")
            return

        classified = sync.classify_events(events_data)
        
        # Save all data to single JSON file
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
        
        sync.save_to_json(all_data, 'polymarket_data.json')
        
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await sync.close()


if __name__ == "__main__":
    asyncio.run(main())
