CREATE TABLE IF NOT EXISTS data_differences (
    id SERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    differences_data JSONB NOT NULL,
    compared_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, compared_at)
);

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

CREATE INDEX IF NOT EXISTS idx_data_differences_event_id ON data_differences(event_id);
CREATE INDEX IF NOT EXISTS idx_data_differences_compared_at ON data_differences(compared_at DESC);

CREATE INDEX IF NOT EXISTS idx_market_differences_market_id ON market_differences(market_id);
CREATE INDEX IF NOT EXISTS idx_market_differences_event_id ON market_differences(event_id);
CREATE INDEX IF NOT EXISTS idx_market_differences_compared_at ON market_differences(compared_at DESC);

CREATE OR REPLACE VIEW recent_event_differences AS
SELECT 
    dd.id,
    dd.event_id,
    e.title as event_title,
    dd.differences_data,
    dd.compared_at,
    dd.created_at
FROM data_differences dd
JOIN events e ON dd.event_id = e.id
ORDER BY dd.compared_at DESC;

CREATE OR REPLACE VIEW recent_market_differences AS
SELECT 
    md.id,
    md.market_id,
    md.event_id,
    e.title as event_title,
    m.question as market_question,
    md.differences_data,
    md.compared_at,
    md.created_at
FROM market_differences md
JOIN events e ON md.event_id = e.id
JOIN markets m ON md.market_id = m.id
ORDER BY md.compared_at DESC;
