# Polymart Financial Data Pipeline

A production-ready Python pipeline for fetching, filtering, and storing Polymarket financial data with PostgreSQL integration.

## Features

- **Real-time Data Sync**: Fetches live Polymarket events and markets
- **Smart Filtering**: Focuses on US/Crypto/Fed/War events with volume ≥$5M
- **PostgreSQL Integration**: Stores data in normalized database tables
- **Async Processing**: High-performance async HTTP client
- **Data Classification**: Automatically categorizes financial, crypto, and political events

## Tech Stack

- **Python 3.8+** with async/await
- **httpx** - Async HTTP client
- **PostgreSQL** - Database storage
- **SQLAlchemy** - ORM (optional)
- **Pydantic** - Data validation

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database**:
   ```bash
   psql -d polymarket_db -f create_tables.sql
   ```

3. **Run Data Sync**:
   ```bash
   python3 fetch_data.py
   ```

4. **Generate SQL from JSON**:
   ```bash
   python3 json_to_sql.py
   ```

## Data Filtering

- **US Politics**: Trump, elections, government shutdowns
- **Crypto**: Bitcoin, Ethereum, major cryptocurrencies
- **Fed Policy**: Interest rates, FOMC decisions, Powell
- **War/Conflict**: Ukraine, Russia, Israel, geopolitical events
- **Volume Threshold**: Events ≥$5M, Markets ≥$5M 24hr volume

## Database Schema

- **events**: Main event data with classification flags
- **markets**: Individual market questions and outcomes
- **data_sync_log**: Sync history and statistics

## Files

- `fetch_data.py` - Main data fetching and processing
- `config.py` - Configuration settings
- `create_tables.sql` - Database schema
- `json_to_sql.py` - JSON to SQL converter
- `requirements.txt` - Python dependencies

## License

MIT License