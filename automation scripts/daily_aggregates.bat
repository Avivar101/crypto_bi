@echo off
cd /d "C:\Users\user\Documents\Power BI Desktop\Projects\Crypto BI\data_ingestion"
"C:\Users\user\Documents\Power BI Desktop\Projects\Crypto BI\.venv\Scripts\python.exe" daily_aggregates.py >> "C:\Users\user\Documents\Power BI Desktop\Projects\Crypto BI\logs\aggregate_log.txt" 2>&1