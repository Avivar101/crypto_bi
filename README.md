## Project Overview

## Stack Used

## Setup Instructions

## Folder Explanation

## Sample Quries/Visuals

---

# Project Title: Crypto Insights BI

# Objective

To track, analyze and visualize cryptocurrency trends (e.g, price, volume, market cap) with scheduled batch ingestion, clean SQL modeling, and Power BI dashboard.

# Tech Stack

<table><tbody><tr><td><strong>Layer</strong></td><td><strong>Tech/Tool</strong></td></tr><tr><td>Data Source</td><td>Coingecko API</td></tr><tr><td>ETL Scripts</td><td>Python</td></tr><tr><td>Storage</td><td>PostgreSQL</td></tr></tr><tr><td>Reporting</td><td>Power BI</td></tr><tr><td>Automation</td><td>Task Scheduler</td></tr></tbody></table>

# Automation Scripts

<table><tbody><tr><td><strong>Script</strong></td><td><strong>Interval</strong></td><td><strong>Task</strong></td></tr><tr><td>run_etl.bat</td><td>Every 15 mins</td><td>fetches and stores raw crypto data</td></tr><tr><td>daily_aggregates.bat</td><td>Once daily (23:59)</td><td>calculates and inserts daily crypto aggregates</td></tr></tbody></table>
