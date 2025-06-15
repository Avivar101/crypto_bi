@echo off
cd /d "C:\Users\user\Documents\Power BI Desktop\Projects\crypto_bi\data_ingestion"
"C:\Users\user\Documents\Power BI Desktop\Projects\crypto_bi\.venv\Scripts\python.exe" daily_aggregates.py >> "C:\Users\user\Documents\Power BI Desktop\Projects\crypto_bi\logs\aggregate_logs.txt" 2>&1