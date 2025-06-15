INSERT INTO daily_aggregates (
    coin_id,
    date,
    avg_price_usd, max_price_usd, min_price_usd,
    total_volume_usd, avg_price_ngn, max_price_ngn,
    min_price_ngn, total_volume_ngn
    )
SELECT
    coin_id,
    timestamp_utc::date AS date,
    AVG(price_usd),
    MAX(price_usd),
    MIN(price_usd),
    SUM(volume_24h_usd),
    AVG(price_ngn),
    MAX(price_ngn),
    MIN(price_ngn),
    SUM(volume_24h_ngn)
FROM raw_prices
GROUP BY coin_id, timestamp_utc::date
ON CONFLICT (coin_id, date) DO UPDATE
SET
    avg_price_usd = EXCLUDED.avg_price_usd,
    max_price_usd = EXCLUDED.max_price_usd,
    min_price_usd = EXCLUDED.min_price_usd,
    avg_price_ngn = EXCLUDED.avg_price_ngn,
    max_price_ngn = EXCLUDED.max_price_ngn,
    min_price_ngn = EXCLUDED.min_price_ngn,
    total_volume_usd = EXCLUDED.total_volume_usd,
    total_volume_ngn = EXCLUDED.total_volume_ngn;