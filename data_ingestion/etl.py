import sys
import requests
import psycopg2
import time
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta

api_key = '1c5d358c5f17e4ded509d894'

# fetch crypto data
def fetch_prices(currency):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency":currency,
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "true",
        "price_change_percentage": "7d"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error: Failed to fetch crypto prices from API")
        sys.exit(1)

# fetch market summary data
def fetch_market_sum():
    url = "https://api.coingecko.com/api/v3/global"
    headers = {"accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error: Failed to fetch market sum data from API")
        sys.exit(1)

# fetch fear/gread index
def fetch_fear_greed():
    url = "https://api.alternative.me/fng/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['data'][0]
    except requests.exceptions.RequestException as e:
        print("Error: Failed to fetch fear/greed data from API")
        sys.exit(1)

# transform market summary data
def transform_market_cap_sum(data):
    try:
        pct_change_usd = data['data']['market_cap_change_percentage_24h_usd']
        return {
            "market_cap_change_pct_24h": round(pct_change_usd, 2),
            "timestamp_utc": datetime.fromtimestamp(data['data']['updated_at'])  # UNIX timestamp
        }
    except (KeyError, TypeError) as e:
        print("Error: Failed to parse market cap change data")
        return None

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
            'sparkline_ngn': ngn_info.get('sparkline_in_7d', {}).get('price', []),
            'price_percentage_change_7d': coin.get('price_change_percentage_7d_in_currency')
        })
    return merged_data

# Get coin pair
def get_top_pair_for_coin(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/tickers?include_exchange_logo=true"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tickers = response.json()["tickers"]
        tickers_sorted = sorted(tickers, key=lambda x: float(x.get("volume", 0)), reverse=True)
        top_pairs = tickers_sorted[:3] if tickers_sorted else None
        results = []
        for top in top_pairs:
            results.append({
                "base": top["base"],
                "target": top["target"],
                "market": top["market"]["name"],
                "market_logo": top["market"]["logo"],
                "volume_usd": top["converted_volume"]["usd"],
                "target_coin_id": top.get("target_coin_id")
            }) if top else None
        return results
    except requests.exceptions.RequestException as e:
        print("Error: Failed to fetch top coin data from API")
        sys.exit(1)

# top coin pair
def get_top_coins_and_pairs(market_data_usd, limit=3):
    exchange_rate = get_usd_to_ngn_rate(api_key)
    top_coins_usd = market_data_usd[:limit]
    results = []

    for coin in top_coins_usd:
        print(coin['id'])
        pairs = get_top_pair_for_coin(coin["id"])  # Your custom logic
        
        for pair in pairs:
            volume_usd = pair["volume_usd"] if pair else 0
            print(volume_usd, exchange_rate)
            volume_ngn = round(volume_usd * exchange_rate, 2) if volume_usd else 0
            results.append({
                "coin_id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "volume_24h_usd": volume_usd,
                "volume_24h_ngn": volume_ngn,
                "top_pair": pair
            })
            time.sleep(4.5)
    return results

# get ngn/usd rate
def get_usd_to_ngn_rate(api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for HTTP issues
        data = response.json()

        if data['result'] != 'success':
            raise Exception(f"API Error: {data.get('error-type', 'Unknown error')}")

        ngn_rate = data['conversion_rates'].get('NGN')
        if ngn_rate is None:
            raise Exception("NGN rate not found in response.")
        
        return ngn_rate
    
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

def insert_top_coin_pairs(coin_pairs_data):
    formatted_data = []

    for item in coin_pairs_data:
        pair = item["top_pair"]
        if not pair:
            continue  # Skip if no top pair info

        formatted_data.append({
            "coin_id": item["coin_id"],
            "symbol": item["symbol"],
            "name": item["name"],
            "volume_24h_usd": item["volume_24h_usd"],
            "volume_24h_ngn": item["volume_24h_ngn"],
            "base": pair["base"],
            "target": pair["target"],
            "market": pair["market"],
            "market_logo_url": pair["market_logo"],
            "target_coin_id": pair["target_coin_id"],
            "timestamp_utc": datetime.now()
        })
    print(formatted_data)
    return formatted_data

# load into postgres
def load_to_postgres(data, market_data, fear_greed, top_coins):
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
                  timestamp_utc, price_change_pct_24h, market_cap_change_pct_24h, ath_usd, ath_ngn,
                  price_percentage_change_7d
                  ) VALUES (
                  %(id)s, %(price_usd)s, %(price_ngn)s, %(market_cap_usd)s, %(market_cap_ngn)s,
                  %(volume_24h_usd)s, %(volume_24h_ngn)s, %(total_supply)s,
                  %(circulating_supply)s, %(timestamp_utc)s, %(price_change_pct_24h)s, 
                  %(market_cap_change_pct_24h)s, %(ath_usd)s, %(ath_ngn)s, %(price_percentage_change_7d)s
                  )
                  ON CONFLICT (coin_id, price_date) DO UPDATE
                  SET
                    price_usd = EXCLUDED.price_usd,
                    price_ngn = EXCLUDED.price_ngn,
                    market_cap_usd = EXCLUDED.market_cap_usd,
                    market_cap_ngn = EXCLUDED.market_cap_ngn,
                    volume_24h_usd = EXCLUDED.volume_24h_usd,
                    volume_24h_ngn = EXCLUDED.volume_24h_ngn,
                    total_supply = EXCLUDED.total_supply,
                    circulating_supply = EXCLUDED.circulating_supply,
                    timestamp_utc = EXCLUDED.timestamp_utc,
                    price_change_pct_24h = EXCLUDED.price_change_pct_24h,
                    market_cap_change_pct_24h = EXCLUDED.market_cap_change_pct_24h,
                    ath_usd = EXCLUDED.ath_usd,
                    ath_ngn = EXCLUDED.ath_ngn,
                    price_percentage_change_7d = EXCLUDED.price_percentage_change_7d;
                  """, data)
    
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

    # insert into coin_sparkline
    sparkline_rows = []
    start_time = datetime.now() - timedelta(hours=167)  # assuming 168 points

    for coin in data:
        coin_id = coin['id']
        sparkline_usd = coin.get('sparkline_usd', [])

        for i, price in enumerate(sparkline_usd):
            timestamp = start_time + timedelta(hours=i)
            sparkline_rows.append((coin_id, 'USD', timestamp, price))
    
    cur.execute("DELETE FROM coin_sparklines")

    execute_batch(cur, """
        INSERT INTO coin_sparklines (coin_id, currency, timestamp_utc, price)
        VALUES (%s, %s, %s, %s)
    """, sparkline_rows)

    # insert market summary data
    cur.execute("""
            INSERT INTO market_summary (timestamp_utc, market_cap_change_pct_24h)
            VALUES (%s, %s)
            ON CONFLICT (timestamp_utc) DO UPDATE
            SET market_cap_change_pct_24h = EXCLUDED.market_cap_change_pct_24h;
        """, (market_data['timestamp_utc'], market_data['market_cap_change_pct_24h']))

    # insert fear/greed data
    converted_ts = datetime.fromtimestamp(int(fear_greed['timestamp']))
    cur.execute(""" 
                INSERT INTO market_sentiment (value, value_classification, timestamp)
                VALUES (%s, %s, %s)
                ON CONFLICT (timestamp) DO UPDATE
                SET
                    value = EXCLUDED.value,
                    value_classification = EXCLUDED.value_classification;                
                """, (fear_greed['value'], fear_greed['value_classification'], converted_ts))
    
    # insert top_coins data
    execute_batch(cur, """
        INSERT INTO top_coin_pairs (
            coin_id, symbol, name,
            volume_24h_usd, volume_24h_ngn,
            base, target, market, market_logo_url, target_coin_id, timestamp_utc
        ) VALUES (
            %(coin_id)s, %(symbol)s, %(name)s,
            %(volume_24h_usd)s, %(volume_24h_ngn)s,
            %(base)s, %(target)s, %(market)s, %(market_logo_url)s, %(target_coin_id)s, %(timestamp_utc)s
        )
        ON CONFLICT (coin_id, base, target, price_date) DO UPDATE
        SET
            volume_24h_usd = EXCLUDED.volume_24h_usd,
            volume_24h_ngn = EXCLUDED.volume_24h_ngn,
            base = EXCLUDED.base,
            target = EXCLUDED.target,
            market = EXCLUDED.market,
            market_logo_url = EXCLUDED.market_logo_url,
            target_coin_id = EXCLUDED.target_coin_id,
            timestamp_utc = EXCLUDED.timestamp_utc;
    """, top_coins)


    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":

    # fetch data
    usd_raw = fetch_prices('usd')
    time.sleep(3.5)
    ngn_raw = fetch_prices('ngn')
    time.sleep(3.5)
    market_sum = fetch_market_sum()
    time.sleep(3.5)
    fg_data = fetch_fear_greed()

    # transform data
    transformed = transform_data(usd_raw, ngn_raw)
    market_transformed = transform_market_cap_sum(market_sum)

    top_coins = get_top_coins_and_pairs(usd_raw)
    top_coin_pairs_formatted = insert_top_coin_pairs(top_coins)

    # load to databse
    load_to_postgres(transformed, market_transformed, fg_data, top_coin_pairs_formatted)

    print("Script ran at " + str(datetime.now()) + "\n")
