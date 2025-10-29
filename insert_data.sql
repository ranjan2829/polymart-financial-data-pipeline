INSERT INTO events (
    id, title, description, end_date, active, liquidity, volume, 
    volume24hr, liquidity_clob, resolution_source, is_financial, 
    is_crypto, is_big_event, is_excluded
) VALUES 
(1, 'New York City Mayoral Election', 'Election for NYC Mayor', '2025-12-31T12:00:00Z', true, 23168328.13, 321800613.69, 9683340.69, 23168328.13, '', false, true, true, false),
(2, 'Fed decision in October?', 'Federal Reserve interest rate decision', '2025-10-29T12:00:00Z', true, 6035075.07, 114518101.85, 27657198.97, 6035075.07, '', true, true, true, false),
(3, 'What price will Bitcoin hit in 2025?', 'Bitcoin price prediction for 2025', '2025-12-31T12:00:00Z', true, 5000000.00, 39115022.77, 1000000.00, 5000000.00, '', true, true, false, false)
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    end_date = EXCLUDED.end_date,
    active = EXCLUDED.active,
    liquidity = EXCLUDED.liquidity,
    volume = EXCLUDED.volume,
    volume24hr = EXCLUDED.volume24hr,
    liquidity_clob = EXCLUDED.liquidity_clob,
    resolution_source = EXCLUDED.resolution_source,
    is_financial = EXCLUDED.is_financial,
    is_crypto = EXCLUDED.is_crypto,
    is_big_event = EXCLUDED.is_big_event,
    is_excluded = EXCLUDED.is_excluded,
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO markets (
    id, event_id, question, end_date, liquidity, volume, volume24hr, 
    outcomes, outcome_prices, active, description
) VALUES 
(1, 1, 'Will Zohran Mamdani win the 2025 NYC mayoral election?', '2025-12-31T12:00:00Z', 1000000.00, 50000000.00, 2000000.00, '["Yes", "No"]', '{"Yes": 0.89, "No": 0.11}', true, 'NYC Mayoral Election - Zohran Mamdani'),
(2, 1, 'Will Andrew Cuomo win the 2025 NYC mayoral election?', '2025-12-31T12:00:00Z', 500000.00, 25000000.00, 1000000.00, '["Yes", "No"]', '{"Yes": 0.11, "No": 0.89}', true, 'NYC Mayoral Election - Andrew Cuomo'),
(3, 2, 'Fed decreases interest rates by 25 bps after October', '2025-10-29T12:00:00Z', 2000000.00, 7502589.88, 7502589.88, '["Yes", "No"]', '{"Yes": 0.98, "No": 0.02}', true, 'Fed 25 bps rate cut'),
(4, 2, 'Fed decreases interest rates by 50+ bps after October', '2025-10-29T12:00:00Z', 1500000.00, 8757785.21, 8757785.21, '["Yes", "No"]', '{"Yes": 0.01, "No": 0.99}', true, 'Fed 50+ bps rate cut'),
(5, 2, 'No change in Fed interest rates after October 2025', '2025-10-29T12:00:00Z', 1000000.00, 8360040.82, 8360040.82, '["Yes", "No"]', '{"Yes": 0.01, "No": 0.99}', true, 'Fed no change'),
(6, 3, 'Bitcoin price will be above $100,000 in 2025', '2025-12-31T12:00:00Z', 2000000.00, 20000000.00, 500000.00, '["Yes", "No"]', '{"Yes": 0.65, "No": 0.35}', true, 'Bitcoin $100K+ prediction')
ON CONFLICT (id) DO UPDATE SET
    event_id = EXCLUDED.event_id,
    question = EXCLUDED.question,
    end_date = EXCLUDED.end_date,
    liquidity = EXCLUDED.liquidity,
    volume = EXCLUDED.volume,
    volume24hr = EXCLUDED.volume24hr,
    outcomes = EXCLUDED.outcomes,
    outcome_prices = EXCLUDED.outcome_prices,
    active = EXCLUDED.active,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO data_sync_log (
    total_events, total_volume, total_liquidity, financial_events, 
    crypto_events, politics_war_events, high_volume_events, sync_status
) VALUES (
    25, 1049211271.78, 50000000.00, 9, 4, 14, 25, 'success'
);

SELECT 
    e.title,
    e.volume as event_volume,
    e.volume24hr as event_volume24hr,
    COUNT(m.id) as market_count,
    COALESCE(SUM(m.volume), 0) as total_market_volume,
    COALESCE(SUM(m.volume24hr), 0) as total_market_volume24hr,
    CASE 
        WHEN e.is_financial THEN 'Financial'
        WHEN e.is_crypto THEN 'Crypto'
        WHEN e.is_big_event THEN 'Politics/War'
        ELSE 'Other'
    END as category
FROM events e
LEFT JOIN markets m ON e.id = m.event_id AND m.active = true
WHERE e.active = true
GROUP BY e.id, e.title, e.volume, e.volume24hr, e.is_financial, e.is_crypto, e.is_big_event
ORDER BY e.volume DESC;

SELECT 
    e.title as event_title,
    m.question as market_question,
    m.volume as market_volume,
    m.volume24hr as market_volume24hr,
    m.outcome_prices
FROM events e
JOIN markets m ON e.id = m.event_id
WHERE m.active = true 
    AND m.volume24hr >= 5000000
ORDER BY m.volume24hr DESC;

SELECT 
    e.title,
    e.volume,
    e.volume24hr,
    m.question,
    m.volume as market_volume,
    m.volume24hr as market_volume24hr
FROM events e
JOIN markets m ON e.id = m.event_id
WHERE e.is_financial = true 
    AND e.active = true 
    AND m.active = true
ORDER BY e.volume DESC, m.volume DESC;

SELECT 
    e.title,
    e.volume,
    m.question,
    m.outcome_prices
FROM events e
JOIN markets m ON e.id = m.event_id
WHERE e.is_crypto = true 
    AND e.active = true 
    AND m.active = true
    AND m.question ILIKE '%price%'
ORDER BY e.volume DESC;

SELECT 
    e.title,
    e.volume,
    e.volume24hr,
    m.question,
    m.volume as market_volume
FROM events e
JOIN markets m ON e.id = m.event_id
WHERE e.is_big_event = true 
    AND e.active = true 
    AND m.active = true
ORDER BY e.volume DESC, m.volume DESC;

SELECT 
    sync_timestamp,
    total_events,
    total_volume,
    financial_events,
    crypto_events,
    politics_war_events,
    sync_status
FROM data_sync_log
ORDER BY sync_timestamp DESC
LIMIT 5;

SELECT 
    CASE 
        WHEN is_financial THEN 'Financial'
        WHEN is_crypto THEN 'Crypto'
        WHEN is_big_event THEN 'Politics/War'
        ELSE 'Other'
    END as category,
    COUNT(*) as event_count,
    SUM(volume) as total_volume,
    AVG(volume) as avg_volume,
    MAX(volume) as max_volume,
    SUM(volume24hr) as total_volume24hr
FROM events
WHERE active = true
GROUP BY 
    CASE 
        WHEN is_financial THEN 'Financial'
        WHEN is_crypto THEN 'Crypto'
        WHEN is_big_event THEN 'Politics/War'
        ELSE 'Other'
    END
ORDER BY total_volume DESC;
