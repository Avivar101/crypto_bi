
-- lastest prices view
CREATE OR REPLACE VIEW vw_latest_prices AS
SELECT DISTINCT ON (rp.coin_id)
    rp.coin_id,
    c.symbol,
    c.name,
    rp.price_usd,
    rp.price_ngn,
    rp.market_cap_usd,
    rp.market_cap_ngn,
    rp.volume_24h_usd,
    rp.volume_24h_ngn,
    rp.total_supply,
    rp.circulating_supply,
    rp.timestamp_utc
FROM raw_prices rp
JOIN coin_metadata c ON rp.coin_id = c.id
ORDER BY rp.coin_id, rp.timestamp_utc DESC;

-- price history
CREATE or REPLACE VIEW vw_price_history AS
SELECT
    rp.coin_id,
    c.symbol,
    c.name,
    rp.price_usd,
    rp.price_ngn,
    rp.market_cap_usd,
    rp.market_cap_ngn,
    rp.volume_24h_usd,
    rp.volume_24h_ngn,
    rp.timestamp_utc::date AS date
FROM raw_prices rp
JOIN coin_metadata c ON rp.coin_id = c.id
ORDER BY coin_id, date;

-- last 24h top movers
CREATE or REPLACE VIEW vw_top_movers_24h AS
WITH price_ranked AS (
    SELECT
        rp.coin_id,
        rp.price_usd,
        rp.price_ngn,
        rp.timestamp_utc,
        ROW_NUMBER() OVER (PARTITION BY rp.coin_id ORDER BY rp.timestamp_utc DESC) AS rn
    FROM raw_prices rp
    WHERE rp.timestamp_utc >= NOW() - INTERVAL '1 day'
)
SELECT
    c.name,
    c.symbol,
    MAX(CASE WHEN rn = 1 THEN price_usd END) AS latest_price,
    MIN(CASE WHEN rn > 1 THEN price_usd END) AS price_24h_ago,
    ROUND(
        (MAX(CASE WHEN rn = 1 THEN price_usd END) - MIN(CASE WHEN rn > 1 THEN price_usd END))
        / NULLIF(MIN(CASE WHEN rn > 1 THEN price_usd END), 0) * 100, 2
    ) AS change_pct
FROM price_ranked p
JOIN coin_metadata c ON p.coin_id = c.id
GROUP BY c.name, c.symbol
HAVING COUNT(*) > 1
ORDER BY change_pct DESC;

-- last 1hr top movers
CREATE OR REPLACE VIEW vw_top_movers_1h AS
WITH prices_1h AS (
    SELECT
        coin_id,
        price_usd,
        price_ngn,
        timestamp_utc
    FROM raw_prices
    WHERE timestamp_utc >= now() - INTERVAL '1 hour'
),
latest_prices AS (
    SELECT DISTINCT ON (coin_id)
        coin_id,
        price_usd AS latest_price,
        timestamp_utc AS latest_timestamp
    FROM prices_1h
    ORDER BY coin_id, timestamp_utc DESC
),
earliest_price AS (
    SELECT DISTINCT ON (coin_id)
        coin_id,
        price_usd, AS earliest_price,
        timestamp_utc AS earliest_timestamp
    FROM prices_1h
    ORDER BY coin_id, timestamp_utc ASC
)
SELECT
    l.coin_id,
    c.symbol,
    c.name,
    l.latest_price,
    e.earliest_price,
    ROUND(((l.latest_price - e.earliest_price) / NULLIF(e.earliest_price, 0)) * 100, 2) AS price_change_percent,
    l.latest_timestamp,
    e.earliest_timestamp
FROM latest_prices l
JOIN earliest_price e ON l.coin_id = e.coin_id
JOIN coins_metadata c ON l.coin_id = c.id
WHERE e.earliest_price IS NOT NULL AND l.latest_price IS NOT NULL
ORDER BY ABS(((l.latest_price - e.earliest_price) / NULLIF(e.earliest_price, 0))) DESC
LIMIT 10;

-- current total amrket summary
CREATE OR REPLACE VIEW  vw_market_summary AS
SELECT
    COUNT(DISTINCT coin_id) AS coin_count,
    SUM(market_cap_ngn) AS total_market_cap,
    SUM(volume_24h_ngn) AS total_volume,
    MAX(timestamp_utc) AS last_updated
FROM vw_latest_prices;