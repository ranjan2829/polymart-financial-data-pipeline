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

### Option 1: Monolith Client (Recommended)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database**:
   ```bash
   python3 polymarket_client.py setup
   ```

3. **Fetch Data**:
   ```bash
   python3 polymarket_client.py fetch
   ```

4. **Compare Data**:
   ```bash
   python3 polymarket_client.py compare
   ```

### Option 2: Individual Scripts

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

## Monolith Client Commands

```bash
# Setup database tables
python3 polymarket_client.py setup

# Fetch and process data (saves to JSON)
python3 polymarket_client.py fetch --limit 500

# Compare stored vs fresh data
python3 polymarket_client.py compare

# Verbose logging
python3 polymarket_client.py fetch --verbose

# Help
python3 polymarket_client.py --help
```

## Files

- `polymarket_client.py` - **Monolith client (recommended)**
- `fetch_data.py` - Individual data fetching script
- `compare_data.py` - Individual comparison script
- `config.py` - Configuration settings
- `create_tables.sql` - Database schema
- `comparison_tables.sql` - Comparison tables schema
- `json_to_sql.py` - JSON to SQL converter
- `requirements.txt` - Python dependencies

## License

MIT License