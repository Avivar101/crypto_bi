# Project Title: Crypto Insights BI

# Objective

To track, analyze and visualize cryptocurrency trends (e.g, price, volume, market cap) with scheduled batch ingestion, clean SQL modeling, and Power BI dashboard.

# Tech Stack

<table><tbody><tr><td><strong>Layer</strong></td><td><strong>Tech/Tool</strong></td></tr><tr><td>Data Source</td><td>Coingecko API</td></tr><tr><td>ETL Scripts</td><td>Python</td></tr><tr><td>Storage</td><td>PostgreSQL</td></tr><tr><td>Reporting</td><td>Power BI</td></tr><tr><td>Automation</td><td>Task Scheduler</td></tr></tbody></table>

# Automation Scripts

<table><tbody><tr><td><strong>Script</strong></td><td><strong>Interval</strong></td><td><strong>Task</strong></td></tr><tr><td>run_etl.bat</td><td>Every 15 mins</td><td>fetches and stores raw crypto data</td></tr><tr><td>daily_aggregates.bat</td><td>Once daily (23:59)</td><td>calculates and inserts daily crypto aggregates</td></tr></tbody></table>

# SQL Tables and Views

## Tables

| Table | Description |
| --- | --- |
| Coins | stores metadata for the coins |
| Raw Prices | stores the live prices and values of the coins |
| Daily aggregates | generate and stores aggregate of the coins once a day |

## Views

| views | description |
| --- | --- |
| vw\_latest\_prices | latest prices for each coin in the database |
| vw\_market\_summary | the aggregates of the market (i.e. total market cap) |
| vw\_price\_history | shows time-series history for selected coins |
| vw\_top\_movers\_1h | coins with the biggest 1 hour change |
| vw\_top\_movers\_24h | coins with the biggest 24 hr change |

# Power BI Pages and KPI description

## Page 1: Market Overview

A Snapshot of the market

### Sections:

*   **KPIs**:
    *   Total Market Cap (NGN/USD)
    *   24H Total Volume (NGN/USD)
    *   Number of Coins Tracked
    *   Last Data Refresh TimeStamp
*   **Charts**:
    *   Market Cap line Trend
    *   24H Trading volume line trend
    *   Top gainers (24H)
    *   Table: Coins by rank
    *   Dominance Chart (BTC/ETH/others)
*   **filters**:
    *   Curreny (NGN/USD)

views used: `vw_latest_prices`, `vw_market_summary`, `coin_metadata`

## Page 2: Price Movement and Performance

Track of daily and hourly movements for analyst and traders

### Sections:

*   **KPIs**:
    *   Top Gainers
    *   Top losers
    *   Top week performer
    *   24hr trading volume
*   **Charts**:
    *   Top traded coins by volume
    *   fear/greed gauge
    *   Top volume traded pairs
*   **filters**:
    *   Curreny (NGN/USD)

views used: `vw_latest_prices`, `vw_market_summary`, `coin_metadata`

## Page 3: Coin Detail and History

Drill down into singles coin's price, volume and supply trends

### Sections:

*   **KPIs**:
    *   coin data
    *   coin info
*   **Charts**:
    *   7 day volume bar
    *   coin selector table
    *   Top trading pair
*   **filters**:
    *   Curreny (NGN/USD)

views used: `vw_latest_prices`, `vw_market_summary`, `coin_metadata`