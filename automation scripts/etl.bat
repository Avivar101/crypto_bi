@echo off
cd /d "C:\Users\user\Documents\Power BI Desktop\Projects\crypto_bi\data_ingestion"
"C:\Users\user\Documents\Power BI Desktop\Projects\crypto_bi\.venv\Scripts\python.exe" etl.py >> "C:\Users\user\Documents\Power BI Desktop\Projects\crypto_bi\logs\etl_log.txt" 2>&1