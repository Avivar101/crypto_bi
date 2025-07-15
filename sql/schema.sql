-- Coin metadata table
CREATE TABLE coin_metadata (
    id TEXT PRIMARY KEY,
    symbol TEXT,
    name TEXT,
    image_url TEXT
);

-- Raw prices fetched from API
CREATE TABLE raw_prices (
    id SERIAL PRIMARY KEY,
    coin_id TEXT REFERENCES coin_metadata(id),
    
    price_usd NUMERIC,
    price_ngn NUMERIC,
    market_cap_usd NUMERIC,
    market_cap_ngn NUMERIC,
    volume_24h_usd NUMERIC,
    volume_24h_ngn NUMERIC,
    
    total_supply NUMERIC,
    circulating_supply NUMERIC,
    timestamp_utc TIMESTAMP,
    
    price_change_pct_24h NUMERIC, 
    market_cap_change_pct_24h NUMERIC,
    ath_usd NUMERIC,
    ath_ngn NUMERIC,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    price_date DATE
);

-- Aggregate daily metrics
CREATE TABLE daily_aggregates (
    coin_id TEXT REFERENCES coin_metadata(id),
    date DATE,
    avg_price_usd NUMERIC,
    max_price_usd NUMERIC,
    min_price_usd NUMERIC,
    total_volume_usd NUMERIC,
    avg_price_ngn NUMERIC,
    max_price_ngn NUMERIC,
    min_price_ngn NUMERIC,
    total_volume_ngn NUMERIC,
    PRIMARY KEY (coin_id, date)
);

-- sparkline prices
CREATE TABLE sparkline_prices (
    coin_id TEXT REFERENCES coin_metadata(id),
    timestamp_utc TIMESTAMP,
    price_usd NUMERIC,
    price_ngn NUMERIC,
    PRIMARY KEY (coin_id, timestamp_utc)
);

CREATE TABLE market_summary (
    timestamp_utc TIMESTAMP PRIMARY KEY,
    market_cap_change_pct_24h NUMERIC
);

-- fear/greed
CREATE TABLE market_sentiment (
	id SERIAL PRIMARY KEY,
	value INT,
	value_classification TEXT,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- top coin pairs
CREATE TABLE top_coin_pairs (
    id SERIAL PRIMARY KEY,
    coin_id TEXT REFERENCES coin_metadata(id),
    symbol TEXT,
    name TEXT,
    volume_24h_usd NUMERIC,
    volume_24h_ngn NUMERIC,
    base TEXT,
    target TEXT,
    market TEXT,
	market_logo_url TEXT,
    target_coin_id TEXT,
    timestamp_utc TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    price_date DATE GENERATED ALWAYS AS (timestamp_utc::DATE) STORED,
    UNIQUE (coin_id, price_date)
);

-- Indexes for faster query performance
CREATE INDEX idx_raw_prices_coin_time ON raw_prices (coin_id, timestamp_utc);
CREATE INDEX idx_daily_aggregates_date ON daily_aggregates (date);