#!/usr/bin/env python3

import asyncio
import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
import argparse

import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://ranjanshahajishitole@localhost:5432/polymarket_db"
    openai_api_key: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
logger = logging.getLogger(__name__)


class AIAnalyzer:
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
    
    def fetch_recent_differences(self, limit: int = None, fed_trump_finance_only: bool = False) -> List[Dict[str, Any]]:
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                dd.event_id,
                e.title as event_title,
                e.description as event_description,
                e.is_financial,
                e.is_crypto,
                e.is_big_event,
                dd.differences_data,
                dd.compared_at
            FROM data_differences dd
            JOIN events e ON dd.event_id = e.id
            WHERE dd.compared_at >= NOW() - INTERVAL '24 hours'
        """
        
        if fed_trump_finance_only:
            query += """
                AND (
                    e.is_financial = true 
                    OR e.is_big_event = true
                    OR LOWER(e.title) LIKE '%fed%' 
                    OR LOWER(e.title) LIKE '%federal reserve%'
                    OR LOWER(e.title) LIKE '%trump%'
                    OR LOWER(e.title) LIKE '%fomc%'
                )
            """
        
        query += " ORDER BY dd.compared_at DESC"
        
        if limit:
            query += " LIMIT %s"
            cursor.execute(query, (limit,))
        else:
            cursor.execute(query)
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        cursor.close()
        return results
    
    def extract_key_changes(self, differences_data: Dict[str, Any]) -> Dict[str, Any]:
        changes = {
            'volume_change': None,
            'volume24hr_change': None,
            'liquidity_change': None,
            'liquidity_clob_change': None,
            'significant_events': [],
            'market_metrics': {
                'old_volume': None,
                'new_volume': None,
                'old_liquidity': None,
                'new_liquidity': None,
                'volume_difference': None,
                'liquidity_difference': None
            }
        }
        
        if 'volume' in differences_data and differences_data['volume']:
            vol_data = differences_data['volume']
            if isinstance(vol_data, dict):
                percent_change = vol_data.get('percent_change', 0)
                old_vol = vol_data.get('old', 0)
                new_vol = vol_data.get('new', 0)
                diff = vol_data.get('difference', 0)
                
                changes['volume_change'] = {
                    'percent_change': percent_change,
                    'direction': 'up' if percent_change > 0 else 'down',
                    'old_value': old_vol,
                    'new_value': new_vol,
                    'absolute_change': diff
                }
                changes['market_metrics']['old_volume'] = old_vol
                changes['market_metrics']['new_volume'] = new_vol
                changes['market_metrics']['volume_difference'] = diff
                
                if abs(percent_change) > 0.5:
                    changes['significant_events'].append(f"Volume {'increased' if percent_change > 0 else 'decreased'} by {abs(percent_change):.1f}% (${diff:,.0f})")
        
        if 'volume24hr' in differences_data and differences_data['volume24hr']:
            vol24_data = differences_data['volume24hr']
            if isinstance(vol24_data, dict):
                percent_change = vol24_data.get('percent_change', 0)
                old_vol = vol24_data.get('old', 0)
                new_vol = vol24_data.get('new', 0)
                diff = vol24_data.get('difference', 0)
                
                changes['volume24hr_change'] = {
                    'percent_change': percent_change,
                    'direction': 'up' if percent_change > 0 else 'down',
                    'old_value': old_vol,
                    'new_value': new_vol,
                    'absolute_change': diff
                }
                
                if abs(percent_change) > 1:
                    changes['significant_events'].append(f"24h Volume {'increased' if percent_change > 0 else 'decreased'} by {abs(percent_change):.1f}% (${diff:,.0f})")
        
        if 'liquidity' in differences_data and differences_data['liquidity']:
            liq_data = differences_data['liquidity']
            if isinstance(liq_data, dict):
                percent_change = liq_data.get('percent_change', 0)
                old_liq = liq_data.get('old', 0)
                new_liq = liq_data.get('new', 0)
                diff = liq_data.get('difference', 0)
                
                changes['liquidity_change'] = {
                    'percent_change': percent_change,
                    'direction': 'up' if percent_change > 0 else 'down',
                    'old_value': old_liq,
                    'new_value': new_liq,
                    'absolute_change': diff
                }
                changes['market_metrics']['old_liquidity'] = old_liq
                changes['market_metrics']['new_liquidity'] = new_liq
                changes['market_metrics']['liquidity_difference'] = diff
                
                if abs(percent_change) > 2:
                    changes['significant_events'].append(f"Liquidity {'increased' if percent_change > 0 else 'decreased'} by {abs(percent_change):.1f}% (${diff:,.0f})")
        
        if 'liquidity_clob' in differences_data and differences_data['liquidity_clob']:
            clob_data = differences_data['liquidity_clob']
            if isinstance(clob_data, dict):
                percent_change = clob_data.get('percent_change', 0)
                old_clob = clob_data.get('old', 0)
                new_clob = clob_data.get('new', 0)
                diff = clob_data.get('difference', 0)
                
                changes['liquidity_clob_change'] = {
                    'percent_change': percent_change,
                    'direction': 'up' if percent_change > 0 else 'down',
                    'old_value': old_clob,
                    'new_value': new_clob,
                    'absolute_change': diff
                }
                
                if abs(percent_change) > 5:
                    changes['significant_events'].append(f"CLOB Liquidity {'increased' if percent_change > 0 else 'decreased'} by {abs(percent_change):.1f}% (${diff:,.0f})")
        
        return changes
    
    def categorize_topic(self, event_data: Dict[str, Any]) -> str:
        if event_data.get('is_crypto'):
            return 'crypto'
        elif event_data.get('is_financial'):
            return 'financial'
        elif event_data.get('is_big_event'):
            return 'politics_war'
        else:
            return 'other'
    
    async def get_ai_analysis(self, event_title: str, event_description: str, changes: Dict[str, Any], topic: str) -> str:
        if not settings.openai_api_key:
            return "OpenAI API key not configured. Please set OPENAI_API_KEY in .env file."
        
        try:
            prompt = f"""
Analyze this Polymarket event and provide comprehensive market insights:

TOPIC: {event_title}
DESCRIPTION: {event_description[:300]}...
CATEGORY: {topic.upper()}

DETAILED MARKET CHANGES:
{', '.join(changes.get('significant_events', ['No significant changes']))}

MARKET METRICS:
- Volume: ${changes.get('market_metrics', {}).get('old_volume', 0) or 0:,.0f} → ${changes.get('market_metrics', {}).get('new_volume', 0) or 0:,.0f}
- Liquidity: ${changes.get('market_metrics', {}).get('old_liquidity', 0) or 0:,.0f} → ${changes.get('market_metrics', {}).get('new_liquidity', 0) or 0:,.0f}

Provide a comprehensive, detailed analysis covering:
1. What specific market activity occurred and the magnitude (include specific numbers)
2. Potential drivers and catalysts for these changes (what might have caused this)
3. Market sentiment implications and trader behavior (what traders are thinking/doing)
4. Risk assessment and future outlook (what could happen next)

Be specific, detailed, and provide actionable insights. Use the actual numbers and data provided. Write 4-5 complete sentences with comprehensive analysis.
"""
            
            headers = {
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                logger.debug(f"OpenAI response received: {len(ai_response)} characters")
                if not ai_response or len(ai_response) < 10:
                    logger.warning("OpenAI returned empty or very short response")
                    return "OpenAI API returned an empty response. Please try again."
                return ai_response
            else:
                error_text = response.text if hasattr(response, 'text') else 'Unknown error'
                logger.error(f"OpenAI API error: {response.status_code} - {error_text}")
                return f"OpenAI API error {response.status_code}: {error_text}"
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return f"OpenAI API error: {str(e)}. Please check your connection and API key."
    
    
    async def analyze_events(self, limit: int = None, fed_trump_finance_only: bool = False) -> List[Dict[str, Any]]:
        limit_text = f"{limit} events" if limit else "all events"
        filter_text = " (Fed/Trump/Finance only)" if fed_trump_finance_only else ""
        logger.info(f"Fetching recent differences for {limit_text}{filter_text}...")
        events = self.fetch_recent_differences(limit, fed_trump_finance_only)
        logger.info(f"Found {len(events)} events with recent changes")
        
        analyzed_events = []
        
        for event in events:
            try:
                logger.info(f"Analyzing: {event.get('event_title', 'Unknown')}")
                
                differences_data = event.get('differences_data', {})
                changes = self.extract_key_changes(differences_data)
                
                topic = self.categorize_topic(event)
                
                ai_analysis = await self.get_ai_analysis(
                    event.get('event_title', ''),
                    event.get('event_description', ''),
                    changes,
                    topic
                )
                
                analysis = {
                    'topic': event.get('event_title'),
                    'description': event.get('event_description', '')[:200] + '...',
                    'category': topic,
                    'event_id': event.get('event_id'),
                    'compared_at': event.get('compared_at').isoformat() if event.get('compared_at') else None,
                    'market_changes': changes,
                    'ai_analysis': ai_analysis,
                    'classification': {
                        'is_crypto': event.get('is_crypto', False),
                        'is_financial': event.get('is_financial', False),
                        'is_big_event': event.get('is_big_event', False)
                    }
                }
                
                analyzed_events.append(analysis)
                logger.info(f"Analysis complete for: {event.get('event_title')}")
                
            except Exception as e:
                logger.error(f"Error analyzing event {event.get('event_id', 'unknown')}: {e}")
                continue
        
        return analyzed_events
    
    def save_analysis(self, analysis_data: List[Dict[str, Any]], filename: str = 'ai_market_analysis.json'):
        output = {
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'total_topics_analyzed': len(analysis_data),
            'topics': analysis_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"AI analysis saved to {filename}")
        return output


async def main():
    parser = argparse.ArgumentParser(description='AI-Powered Polymarket Analysis')
    parser.add_argument('--limit', type=int, default=None, help='Number of events to analyze (default: all)')
    parser.add_argument('--output', type=str, default='ai_market_analysis.json', help='Output JSON filename')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--fed-trump-finance', action='store_true', help='Only analyze Fed, Trump, and Finance events')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    analyzer = AIAnalyzer()
    
    try:
        analysis_data = await analyzer.analyze_events(args.limit, args.fed_trump_finance)
        output = analyzer.save_analysis(analysis_data, args.output)
        
        print(f"\n=== AI ANALYSIS COMPLETE ===")
        print(f"Topics analyzed: {output['total_topics_analyzed']}")
        print(f"Results saved to: {args.output}")
        
        print(f"\n=== AI INSIGHTS ===")
        for topic in analysis_data:
            print(f"\n📊 {topic['topic']} ({topic['category'].upper()})")
            print(f"🤖 AI Analysis: {topic['ai_analysis']}")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
    finally:
        await analyzer.close()


if __name__ == "__main__":
    asyncio.run(main())
