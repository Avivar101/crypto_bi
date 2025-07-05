
-- lastest prices view
CREATE OR REPLACE VIEW vw_latest_prices AS
WITH latest_per_coin AS (
    SELECT DISTINCT ON (coin_id)
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
	    rp.timestamp_utc,
        rp.price_change_pct_24h,
        rp.market_cap_change_pct_24h
    FROM raw_prices rp
	JOIN coin_metadata c ON rp.coin_id = c.id
    ORDER BY rp.coin_id, rp.timestamp_utc DESC
)

SELECT
    lp.*,
    ROW_NUMBER() OVER (ORDER BY market_cap_usd DESC) AS coin_rank
FROM latest_per_coin lp

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
CREATE OR REPLACE VIEW vw_top_movers_24h AS
SELECT DISTINCT ON (rp.coin_id)
    rp.coin_id,
    c.symbol,
    c.name,
    rp.price_usd,
	rp.price_ngn,
    rp.price_change_pct_24h,
    c.image_url
FROM raw_prices rp
JOIN coin_metadata c ON rp.coin_id = c.id
WHERE rp.price_change_pct_24h IS NOT NULL 
	AND rp.price_change_pct_24h > 0 
ORDER BY rp.coin_id, rp.timestamp_utc DESC, rp.price_change_pct_24h DESC;

-- current total amrket summary
CREATE OR REPLACE VIEW  vw_market_summary AS
SELECT
    COUNT(DISTINCT coin_id) AS coin_count,
    SUM(market_cap_ngn) AS total_market_cap,
    SUM(volume_24h_ngn) AS total_volume,
    MAX(timestamp_utc) AS last_updated
FROM vw_latest_prices;