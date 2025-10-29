#!/usr/bin/env python3
"""
Simple Polymarket Data Analysis
Analyzes data changes and generates insights for crypto and global markets
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
import argparse

import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://ranjanshahajishitole@localhost:5432/polymarket_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
logger = logging.getLogger(__name__)


class SimpleAnalyzer:
    def __init__(self):
        self.db_conn = None
    
    def close(self):
        if self.db_conn:
            self.db_conn.close()
    
    def get_db_connection(self):
        if not self.db_conn or self.db_conn.closed:
            self.db_conn = psycopg2.connect(settings.database_url)
        return self.db_conn
    
    def fetch_recent_differences(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent differences for analysis"""
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
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
            ORDER BY dd.compared_at DESC
            LIMIT %s
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        cursor.close()
        return results
    
    def extract_metrics(self, differences_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from differences data"""
        metrics = {
            'volume_change': None,
            'volume24hr_change': None,
            'liquidity_change': None,
            'significant_changes': []
        }
        
        # Volume change
        if 'volume' in differences_data and differences_data['volume']:
            vol_data = differences_data['volume']
            if isinstance(vol_data, dict):
                metrics['volume_change'] = {
                    'old': vol_data.get('old', 0),
                    'new': vol_data.get('new', 0),
                    'difference': vol_data.get('difference', 0),
                    'percent_change': vol_data.get('percent_change', 0)
                }
                if abs(vol_data.get('percent_change', 0)) > 5:
                    metrics['significant_changes'].append(f"Volume changed by {vol_data.get('percent_change', 0):.2f}%")
        
        # 24h Volume change
        if 'volume24hr' in differences_data and differences_data['volume24hr']:
            vol24_data = differences_data['volume24hr']
            if isinstance(vol24_data, dict):
                metrics['volume24hr_change'] = {
                    'old': vol24_data.get('old', 0),
                    'new': vol24_data.get('new', 0),
                    'difference': vol24_data.get('difference', 0),
                    'percent_change': vol24_data.get('percent_change', 0)
                }
                if abs(vol24_data.get('percent_change', 0)) > 10:
                    metrics['significant_changes'].append(f"24h Volume changed by {vol24_data.get('percent_change', 0):.2f}%")
        
        # Liquidity change
        if 'liquidity' in differences_data and differences_data['liquidity']:
            liq_data = differences_data['liquidity']
            if isinstance(liq_data, dict):
                metrics['liquidity_change'] = {
                    'old': liq_data.get('old', 0),
                    'new': liq_data.get('new', 0),
                    'difference': liq_data.get('difference', 0),
                    'percent_change': liq_data.get('percent_change', 0)
                }
                if abs(liq_data.get('percent_change', 0)) > 10:
                    metrics['significant_changes'].append(f"Liquidity changed by {liq_data.get('percent_change', 0):.2f}%")
        
        return metrics
    
    def categorize_market(self, event_data: Dict[str, Any]) -> str:
        """Categorize market type"""
        if event_data.get('is_crypto'):
            return 'crypto'
        elif event_data.get('is_financial'):
            return 'financial'
        elif event_data.get('is_big_event'):
            return 'politics_war'
        else:
            return 'other'
    
    def generate_insight(self, event_data: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Generate market insight based on data"""
        category = self.categorize_market(event_data)
        
        # Simple insight generation based on metrics
        insights = []
        
        if metrics.get('volume_change'):
            vol_change = metrics['volume_change']['percent_change']
            if vol_change > 10:
                insights.append(f"Strong bullish momentum with {vol_change:.1f}% volume increase")
            elif vol_change > 5:
                insights.append(f"Moderate positive sentiment with {vol_change:.1f}% volume growth")
            elif vol_change < -10:
                insights.append(f"Bearish pressure with {vol_change:.1f}% volume decline")
            elif vol_change < -5:
                insights.append(f"Negative sentiment with {vol_change:.1f}% volume drop")
            else:
                insights.append(f"Stable volume with {vol_change:.1f}% change")
        
        if metrics.get('liquidity_change'):
            liq_change = metrics['liquidity_change']['percent_change']
            if liq_change > 20:
                insights.append(f"High liquidity injection of {liq_change:.1f}%")
            elif liq_change < -20:
                insights.append(f"Significant liquidity withdrawal of {liq_change:.1f}%")
        
        if category == 'crypto':
            insights.append("Crypto market dynamics suggest high volatility and speculative interest")
        elif category == 'financial':
            insights.append("Financial market shows institutional trading patterns")
        elif category == 'politics_war':
            insights.append("Geopolitical events driving market uncertainty and hedging activity")
        
        if not insights:
            insights.append("Market showing minimal activity with stable conditions")
        
        return " | ".join(insights)
    
    def analyze_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Analyze events and generate insights"""
        logger.info(f"Fetching recent differences for {limit} events...")
        events = self.fetch_recent_differences(limit)
        logger.info(f"Found {len(events)} events with recent changes")
        
        analyzed_events = []
        
        for event in events:
            try:
                logger.info(f"Analyzing event: {event.get('event_title', 'Unknown')}")
                
                # Extract metrics
                differences_data = event.get('differences_data', {})
                metrics = self.extract_metrics(differences_data)
                
                # Categorize market
                category = self.categorize_market(event)
                
                # Generate insight
                insight = self.generate_insight(event, metrics)
                
                # Compile analysis
                analysis = {
                    'event_id': event.get('event_id'),
                    'event_title': event.get('event_title'),
                    'event_description': event.get('event_description', '')[:200] + '...',
                    'category': category,
                    'compared_at': event.get('compared_at').isoformat() if event.get('compared_at') else None,
                    'metrics': metrics,
                    'insight': insight,
                    'is_crypto': event.get('is_crypto', False),
                    'is_financial': event.get('is_financial', False),
                    'is_big_event': event.get('is_big_event', False)
                }
                
                analyzed_events.append(analysis)
                logger.info(f"Analysis complete for event {event.get('event_id')}")
                
            except Exception as e:
                logger.error(f"Error analyzing event {event.get('event_id', 'unknown')}: {e}")
                continue
        
        return analyzed_events
    
    def save_analysis(self, analysis_data: List[Dict[str, Any]], filename: str = 'market_insights.json'):
        """Save analysis results to JSON"""
        output = {
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'total_events_analyzed': len(analysis_data),
            'crypto_events': len([e for e in analysis_data if e.get('is_crypto')]),
            'financial_events': len([e for e in analysis_data if e.get('is_financial')]),
            'politics_war_events': len([e for e in analysis_data if e.get('is_big_event')]),
            'events': analysis_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis saved to {filename}")
        return output


def main():
    parser = argparse.ArgumentParser(description='Simple Polymarket Data Analysis')
    parser.add_argument('--limit', type=int, default=10, help='Number of events to analyze')
    parser.add_argument('--output', type=str, default='market_insights.json', help='Output JSON filename')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    analyzer = SimpleAnalyzer()
    
    try:
        analysis_data = analyzer.analyze_events(args.limit)
        output = analyzer.save_analysis(analysis_data, args.output)
        
        print(f"\n=== ANALYSIS COMPLETE ===")
        print(f"Events analyzed: {output['total_events_analyzed']}")
        print(f"Crypto events: {output['crypto_events']}")
        print(f"Financial events: {output['financial_events']}")
        print(f"Politics/War events: {output['politics_war_events']}")
        print(f"Results saved to: {args.output}")
        
        # Print insights
        print(f"\n=== INSIGHTS ===")
        for event in analysis_data:
            print(f"\n{event['event_title']} ({event['category'].upper()})")
            print(f"Insight: {event['insight']}")
            if event['metrics']['significant_changes']:
                print(f"Changes: {', '.join(event['metrics']['significant_changes'])}")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
