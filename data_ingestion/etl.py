import sys
import requests
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta

# fetch crypto data
def fetch_prices(currency):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency":currency,
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "true"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error: Failed to fetch prices from API")
        sys.exit(1) 

# transform data
def transform_data(raw_data_usd, raw_data_ngn):
    ngn_map = {coin['id']: coin for coin in raw_data_ngn}
    merged_data = []

    for coin in raw_data_usd:
        coin_id = coin['id']
        ngn_info = ngn_map.get(coin_id, {})

        merged_data.append({
            'id': coin_id,
            'symbol': coin.get('symbol'),
            'name': coin.get('name'),
            'image_url': coin.get('image'),

            'price_usd': coin.get('current_price'),
            'price_ngn': ngn_info.get('current_price'),
            'market_cap_usd': coin.get('market_cap'),
            'market_cap_ngn': ngn_info.get('market_cap'),
            'volume_24h_usd': coin.get('total_volume'),
            'volume_24h_ngn': ngn_info.get('total_volume'),

            'total_supply': coin.get('total_supply'),
            'circulating_supply': coin.get('circulating_supply'),
            'timestamp_utc': datetime.now(),

            'price_change_pct_24h': coin.get('price_change_percentage_24h'),
            'market_cap_change_pct_24h': coin.get('market_cap_change_percentage_24h'),
            'ath_usd': coin.get('ath'),
            'ath_ngn': ngn_info.get('ath'),
            'sparkline_usd': coin.get('sparkline_in_7d', {}).get('price', []),
            'sparkline_ngn': ngn_info.get('sparkline_in_7d', {}).get('price', [])
        })
    return merged_data

# load into postgres
def load_to_postgres(data):
    conn = psycopg2.connect(
        dbname="crypto_analytics",
        user="postgres",
        password="postgresuser",
        host="localhost",
        port="5433"
    )
    cur = conn.cursor()

    # insert coins, ignore duplicates
    coin_ids = set()
    for row in data:
        if row['id'] not in coin_ids:
            cur.execute("""
                        INSERT INTO coin_metadata (id, symbol, name, image_url)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """, (row['id'], row['symbol'], row['name'], row['image_url']))
            coin_ids.add(row['id'])

    # Insert price data
    execute_batch(cur, """
                  INSERT INTO raw_prices (
                  coin_id, price_usd, price_ngn, market_cap_usd, market_cap_ngn, 
                  volume_24h_usd, volume_24h_ngn, total_supply, circulating_supply,
                  timestamp_utc, price_change_pct_24h, market_cap_change_pct_24h, ath_usd, ath_ngn
                  ) VALUES (
                  %(id)s, %(price_usd)s, %(price_ngn)s, %(market_cap_usd)s, %(market_cap_ngn)s,
                  %(volume_24h_usd)s, %(volume_24h_ngn)s, %(total_supply)s,
                  %(circulating_supply)s, %(timestamp_utc)s, %(price_change_pct_24h)s, 
                  %(market_cap_change_pct_24h)s, %(ath_usd)s, %(ath_ngn)s
                  )""", data)
    
    # insert sparkline data
    now = datetime.now()
    interval = timedelta(hours=1)

    for coin in data:
        coin_id = coin['id']
        prices_usd = coin['sparkline_usd']
        prices_ngn = coin['sparkline_ngn']

        # Delete old sparkline for this coin
        cur.execute("DELETE FROM sparkline_prices WHERE coin_id = %s", (coin_id,))

        if len(prices_usd) != len(prices_ngn):
            print(f"Length mismatch for {coin_id}, skipping.")
            continue

        timestamps = [
            now - interval * (len(prices_usd) - 1 - i)
            for i in range(len(prices_usd))
        ]

        for t, usd_price, ngn_price in zip(timestamps, prices_usd, prices_ngn):
            cur.execute("""
                INSERT INTO sparkline_prices (coin_id, timestamp_utc, price_usd, price_ngn)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (coin_id, timestamp_utc) DO NOTHING
            """, (coin_id, t, usd_price, ngn_price))


    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    usd_raw = fetch_prices('usd')
    ngn_raw = fetch_prices('ngn')
    transformed = transform_data(usd_raw, ngn_raw)
    load_to_postgres(transformed)

    print("Script ran at " + str(datetime.now()) + "\n")
