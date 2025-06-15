import psycopg2
from datetime import date, datetime
import os

# --- Configuration ---
DB_PARAMS = {
    "dbname": "crypto_analytics",
    "user": "postgres",
    "password": "postgresuser",
    "host": "localhost",
    "port": 5433,
}

AGGREGATION_SQL = """
INSERT INTO daily_aggregates (
    coin_id,
    date,
    avg_price_usd, max_price_usd, min_price_usd,
    total_volume_usd,
    avg_price_ngn, max_price_ngn, min_price_ngn,
    total_volume_ngn
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
WHERE timestamp_utc::date = CURRENT_DATE - INTERVAL '1 day'
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
"""

def run_daily_aggregation():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute(AGGREGATION_SQL)
        conn.commit()
        print(f"[{date.today()}] Daily aggregation successful.")
    except Exception as e:
        print(f"[{date.today()}] Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_daily_aggregation()
