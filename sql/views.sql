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
        rp.market_cap_change_pct_24h,
        rp.ath_usd,
        rp.ath_ngn
    FROM raw_prices rp
	JOIN coin_metadata c ON rp.coin_id = c.id
    ORDER BY rp.coin_id, rp.timestamp_utc DESC
)

SELECT
    lp.*,
    ROW_NUMBER() OVER (ORDER BY market_cap_usd DESC) AS coin_rank,
    ROUND((lp.market_cap_ngn / NULLIF(SUM(lp.market_cap_ngn), 0)) * 100, 2) AS dominance_pct
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



-- top 7 day gainers
CREATE OR REPLACE VIEW vw_top_7d_gainers AS
WITH ranked_gainers AS (
    SELECT
        rp.coin_id,
        c.symbol,
        c.name,
        rp.price_usd,
        rp.price_ngn,
        c.image_url,
        rp.price_percentage_change_7d,
        ROW_NUMBER() OVER (
            ORDER BY rp.price_percentage_change_7d DESC
        ) AS rn
    FROM raw_prices rp
    JOIN coin_metadata c ON rp.coin_id = c.id
    WHERE rp.price_percentage IS NOT NULL
        AND rp.price_percentage > 0
)
SELECT
    coin_id,
    symbol,
    name,
    price_usd,
    price_ngn,
    image_url,
    price_pecentage_change_7d
FROM ranked_gainers
WHERE rn <= 10;



-- top 7 day losers
CREATE OR REPLACE VIEW vw_top_7d_losers AS
WITH ranked_losers AS (
  SELECT 
    rp.coin_id,
    c.symbol,
    c.name,
    rp.price_usd,
    rp.price_ngn,
    c.image_url,
    rp.price_percentage_change_7d,
    ROW_NUMBER() OVER (
      ORDER BY rp.price_percentage_change_7d ASC
    ) AS rn
  FROM raw_prices rp
  JOIN coin_metadata c ON rp.coin_id = c.id
  WHERE rp.price_percentage_change_7d IS NOT NULL
    AND rp.price_percentage_change_7d < 0
)
SELECT 
  coin_id,
  symbol,
  name,
  price_usd,
  price_ngn,
  image_url,
  price_percentage_change_7d
FROM ranked_losers
WHERE rn <= 10;



-- top traded pairs
CREATE OR REPLACE VIEW vw_top_coin_pairs AS
WITH latest_pairs AS (
    SELECT DISTINCT ON (tcp.symbol)
        tcp.*
    FROM top_coin_pairs tcp
    ORDER BY tcp.symbol, tcp.timestamp_utc DESC
)
SELECT
    lp.base,
    lp.target,
    cm.image_url AS base_image_url,
    cm_target.image_url AS target_coin_image_url,
    lp.volume_24h_usd,
    lp.volume_24h_ngn,
    lp.market,
    lp.market_logo_url
FROM latest_pairs lp
LEFT JOIN coin_metadata cm ON LOWER(lp.base) = cm.symbol
LEFT JOIN coin_metadata cm_target ON LOWER(lp.target) = cm_target.symbol;


-- fear/greed index
CREATE OR REPLACE VIEW vw_fear_greed_index AS
SELECT
    m.value,
    m.value_classification
FROM market_sentiment m
ORDER BY m.timestamp DESC
LIMIT 1;


-- current total market summary
CREATE OR REPLACE VIEW  vw_market_summary AS
SELECT
    COUNT(DISTINCT coin_id) AS coin_count,
    SUM(market_cap_ngn) AS total_market_cap,
    SUM(volume_24h_ngn) AS total_volume,
    MAX(timestamp_utc) AS last_updated
FROM vw_latest_prices;

CREATE OR REPLACE VIEW vw_market_summary AS
WITH latest_market_summary AS (
    SELECT *
    FROM market_summary
    ORDER BY timestamp_utc DESC
    LIMIT 1
)
SELECT
    COUNT(DISTINCT coin_id) AS coin_count,
    SUM(market_cap_ngn) AS total_market_cap,
    SUM(volume_24h_ngn) AS total_volume,
    MAX(lp.timestamp_utc) AS last_updated,
    ms.market_cap_change_pct_24h
FROM vw_latest_prices lp
CROSS JOIN latest_market_summary ms;