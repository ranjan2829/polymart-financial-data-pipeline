# Polymart Financial Data Pipeline

A clean, production-ready system for fetching, analyzing, and generating AI insights on Polymarket financial data.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python3 polymarket_client.py setup

# Fetch and process data
python3 polymarket_client.py fetch --limit 500

# Compare data changes
python3 polymarket_client.py compare

# Generate AI analysis
python3 ai_analyze.py --limit 10
```

## 📁 Project Structure

```
polymart-financial-data-pipeline/
├── polymarket_client.py    # Main client (fetch, compare, setup)
├── ai_analyze.py          # AI analysis with OpenAI
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── create_tables.sql      # Database schema
├── insert_data.sql        # Sample data inserts
├── comparison_tables.sql  # Data comparison tables
└── README.md             # This file
```

## 🛠️ Commands

### Main Client
```bash
# Setup database tables
python3 polymarket_client.py setup

# Fetch and process data
python3 polymarket_client.py fetch --limit 500

# Compare stored vs fresh data
python3 polymarket_client.py compare

# Verbose logging
python3 polymarket_client.py fetch --verbose
```

### AI Analysis
```bash
# Generate AI insights (requires OpenAI API key)
python3 ai_analyze.py --limit 10

# Custom output file
python3 ai_analyze.py --limit 5 --output my_analysis.json

# Verbose logging
python3 ai_analyze.py --limit 10 --verbose
```

## 🔧 Configuration

Set your OpenAI API key in `.env`:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

## 📊 Features

- **Data Fetching**: Fetches US/Crypto/Fed events from Polymarket API
- **Data Processing**: Cleans and filters data (≥$5M volume, active events only)
- **Database Storage**: PostgreSQL with proper schema and indexes
- **Data Comparison**: Tracks changes in volume, liquidity, prices
- **AI Analysis**: Real OpenAI insights on market dynamics
- **Clean Output**: Simple JSON with just topic + AI response

## 🗄️ Database Schema

- `events`: Main event data with classifications
- `markets`: Market details for each event
- `data_differences`: Tracks changes over time
- `market_differences`: Market-level change tracking

## 📈 AI Analysis Output

```json
{
  "analysis_timestamp": "2025-10-29T15:39:23.196916+00:00",
  "total_topics_analyzed": 3,
  "topics": [
    {
      "topic": "Fed decision in December?",
      "category": "crypto",
      "ai_analysis": "The increase in volume and liquidity suggests heightened interest..."
    }
  ]
}
```

## 🎯 Focus Areas

- **US Politics**: Trump-related events, elections
- **Crypto Markets**: Cryptocurrency predictions
- **Fed Decisions**: Federal Reserve policy events
- **War/Conflict**: Geopolitical events

## 📝 Requirements

- Python 3.8+
- PostgreSQL
- OpenAI API key (for AI analysis)
- Internet connection

## 🔄 Workflow

1. **Setup**: Create database tables
2. **Fetch**: Get latest data from Polymarket
3. **Compare**: Track changes over time
4. **Analyze**: Generate AI insights on market dynamics

Clean, simple, and production-ready! 🚀