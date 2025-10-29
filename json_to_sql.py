import json
import sys
from datetime import datetime
from typing import Dict, Any, List

def convert_json_to_sql(json_file: str, output_file: str = None):
    """Convert JSON data to SQL INSERT statements"""
    
    # Read JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    events = data.get('all_events', [])
    summary = data.get('summary', {})
    
    sql_statements = []
    
    
    sql_statements.append("-- Insert events data")
    sql_statements.append("INSERT INTO events (")
    sql_statements.append("    id, title, description, end_date, active, liquidity, volume,")
    sql_statements.append("    volume24hr, liquidity_clob, resolution_source, is_financial,")
    sql_statements.append("    is_crypto, is_big_event, is_excluded")
    sql_statements.append(") VALUES")
    
    event_values = []
    for event in events:
        # Clean and format values
        event_id = event.get('id', 0)
        title = event.get('title', '').replace("'", "''")  # Escape single quotes
        description = (event.get('description', '') or '').replace("'", "''")
        end_date = event.get('endDate', '')
        active = event.get('active', True)
        liquidity = event.get('liquidity', 0) or 0
        volume = event.get('volume', 0) or 0
        volume24hr = event.get('volume24hr', 0) or 0
        liquidity_clob = event.get('liquidityClob', 0) or 0
        resolution_source = (event.get('resolutionSource', '') or '').replace("'", "''")
        is_financial = event.get('is_financial', False)
        is_crypto = event.get('is_crypto', False)
        is_big_event = event.get('is_big_event', False)
        is_excluded = event.get('is_excluded', False)
        
        # Format end_date
        if end_date:
            try:
                # Convert ISO format to PostgreSQL format
                if end_date.endswith('Z'):
                    end_date = end_date.replace('Z', '+00:00')
                # Ensure proper quoting
                end_date = f"'{end_date}'"
            except:
                end_date = 'NULL'
        else:
            end_date = 'NULL'
        
        event_value = f"({event_id}, '{title}', '{description}', {end_date}, {active}, {liquidity}, {volume}, {volume24hr}, {liquidity_clob}, '{resolution_source}', {is_financial}, {is_crypto}, {is_big_event}, {is_excluded})"
        event_values.append(event_value)
    
    # Join event values
    sql_statements.append(",\n".join(event_values))
    sql_statements.append("ON CONFLICT (id) DO UPDATE SET")
    sql_statements.append("    title = EXCLUDED.title,")
    sql_statements.append("    description = EXCLUDED.description,")
    sql_statements.append("    end_date = EXCLUDED.end_date,")
    sql_statements.append("    active = EXCLUDED.active,")
    sql_statements.append("    liquidity = EXCLUDED.liquidity,")
    sql_statements.append("    volume = EXCLUDED.volume,")
    sql_statements.append("    volume24hr = EXCLUDED.volume24hr,")
    sql_statements.append("    liquidity_clob = EXCLUDED.liquidity_clob,")
    sql_statements.append("    resolution_source = EXCLUDED.resolution_source,")
    sql_statements.append("    is_financial = EXCLUDED.is_financial,")
    sql_statements.append("    is_crypto = EXCLUDED.is_crypto,")
    sql_statements.append("    is_big_event = EXCLUDED.is_big_event,")
    sql_statements.append("    is_excluded = EXCLUDED.is_excluded,")
    sql_statements.append("    updated_at = CURRENT_TIMESTAMP;")
    sql_statements.append("")
    
    sql_statements.append("-- Insert markets data")
    sql_statements.append("INSERT INTO markets (")
    sql_statements.append("    id, event_id, question, end_date, liquidity, volume, volume24hr,")
    sql_statements.append("    outcomes, outcome_prices, active, description")
    sql_statements.append(") VALUES")
    
    market_values = []
    market_id = 1
    
    for event in events:
        event_id = event.get('id', 0)
        markets = event.get('markets', [])
        
        for market in markets:
            question = (market.get('question', '') or '').replace("'", "''")
            end_date = market.get('endDate', '')
            liquidity = market.get('liquidity', 0) or 0
            volume = market.get('volume', 0) or 0
            volume24hr = market.get('volume24hr', 0) or 0
            outcomes = json.dumps(market.get('outcomes', []))
            outcome_prices = json.dumps(market.get('outcomePrices', {}))
            active = market.get('active', True)
            description = (market.get('description', '') or '').replace("'", "''")
            
            # Format end_date
            if end_date:
                try:
                    if end_date.endswith('Z'):
                        end_date = end_date.replace('Z', '+00:00')
                    # Ensure proper quoting
                    end_date = f"'{end_date}'"
                except:
                    end_date = 'NULL'
            else:
                end_date = 'NULL'
            
            market_value = f"({market_id}, {event_id}, '{question}', {end_date}, {liquidity}, {volume}, {volume24hr}, '{outcomes}', '{outcome_prices}', {active}, '{description}')"
            market_values.append(market_value)
            market_id += 1
    
    if market_values:
        sql_statements.append(",\n".join(market_values))
        sql_statements.append("ON CONFLICT (id) DO UPDATE SET")
        sql_statements.append("    event_id = EXCLUDED.event_id,")
        sql_statements.append("    question = EXCLUDED.question,")
        sql_statements.append("    end_date = EXCLUDED.end_date,")
        sql_statements.append("    liquidity = EXCLUDED.liquidity,")
        sql_statements.append("    volume = EXCLUDED.volume,")
        sql_statements.append("    volume24hr = EXCLUDED.volume24hr,")
        sql_statements.append("    outcomes = EXCLUDED.outcomes,")
        sql_statements.append("    outcome_prices = EXCLUDED.outcome_prices,")
        sql_statements.append("    active = EXCLUDED.active,")
        sql_statements.append("    description = EXCLUDED.description,")
        sql_statements.append("    updated_at = CURRENT_TIMESTAMP;")
    else:
        sql_statements.append("-- No markets data to insert")
    sql_statements.append("")
    
    sql_statements.append("-- Insert sync log entry")
    sql_statements.append("INSERT INTO data_sync_log (")
    sql_statements.append("    total_events, total_volume, total_liquidity, financial_events,")
    sql_statements.append("    crypto_events, politics_war_events, high_volume_events, sync_status")
    sql_statements.append(") VALUES (")
    sql_statements.append(f"    {summary.get('total_events', 0)},")
    sql_statements.append(f"    {summary.get('total_volume', 0)},")
    sql_statements.append(f"    {summary.get('total_liquidity', 0)},")
    sql_statements.append(f"    {summary.get('financial_events', 0)},")
    sql_statements.append(f"    {summary.get('crypto_events', 0)},")
    sql_statements.append(f"    {summary.get('politics_war_events', 0)},")
    sql_statements.append(f"    {summary.get('high_volume_events', 0)},")
    sql_statements.append("    'success'")
    sql_statements.append(");")
    sql_statements.append("")
    
    
    # Write to output file
    output_content = "\n".join(sql_statements)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output_content)
        print(f"SQL statements written to {output_file}")
    else:
        print(output_content)
    
    return output_content

if __name__ == "__main__":
    json_file = "polymarket_data.json"
    output_file = "polymarket_data_insert.sql"
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    try:
        convert_json_to_sql(json_file, output_file)
        print(f"✅ Successfully converted {json_file} to SQL statements")
        print(f"📁 Output file: {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
