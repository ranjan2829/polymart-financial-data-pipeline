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

CREATE TABLE IF NOT EXISTS data_sync_log (
    id SERIAL PRIMARY KEY,
    sync_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_events INTEGER NOT NULL,
    total_volume DECIMAL(20,2),
    total_liquidity DECIMAL(20,2),
    financial_events INTEGER,
    crypto_events INTEGER,
    politics_war_events INTEGER,
    high_volume_events INTEGER,
    sync_status VARCHAR(20) DEFAULT 'success',
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_active ON events(active);
CREATE INDEX IF NOT EXISTS idx_events_volume ON events(volume DESC);
CREATE INDEX IF NOT EXISTS idx_events_volume24hr ON events(volume24hr DESC);
CREATE INDEX IF NOT EXISTS idx_events_financial ON events(is_financial);
CREATE INDEX IF NOT EXISTS idx_events_crypto ON events(is_crypto);
CREATE INDEX IF NOT EXISTS idx_events_big_event ON events(is_big_event);
CREATE INDEX IF NOT EXISTS idx_events_end_date ON events(end_date);

CREATE INDEX IF NOT EXISTS idx_markets_event_id ON markets(event_id);
CREATE INDEX IF NOT EXISTS idx_markets_volume ON markets(volume DESC);
CREATE INDEX IF NOT EXISTS idx_markets_volume24hr ON markets(volume24hr DESC);
CREATE INDEX IF NOT EXISTS idx_markets_active ON markets(active);

CREATE INDEX IF NOT EXISTS idx_sync_log_timestamp ON data_sync_log(sync_timestamp DESC);

CREATE OR REPLACE FUNCTION update_events_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_events_updated_at();

CREATE OR REPLACE FUNCTION update_markets_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_markets_updated_at
    BEFORE UPDATE ON markets
    FOR EACH ROW
    EXECUTE FUNCTION update_markets_updated_at();

CREATE OR REPLACE VIEW events_with_market_stats AS
SELECT 
    e.*,
    COUNT(m.id) as market_count,
    COALESCE(SUM(m.volume), 0) as total_market_volume,
    COALESCE(SUM(m.volume24hr), 0) as total_market_volume24hr,
    COALESCE(SUM(m.liquidity), 0) as total_market_liquidity
FROM events e
LEFT JOIN markets m ON e.id = m.event_id AND m.active = true
GROUP BY e.id;

CREATE OR REPLACE VIEW high_volume_events AS
SELECT *
FROM events_with_market_stats
WHERE volume >= 5000000
ORDER BY volume DESC;

CREATE OR REPLACE VIEW active_events_recent AS
SELECT *
FROM events_with_market_stats
WHERE active = true
    AND (volume24hr > 0 OR total_market_volume24hr > 0)
ORDER BY COALESCE(volume24hr, total_market_volume24hr) DESC;

