@echo off
cd /d "C:\Users\user\Documents\Power BI Desktop\Projects\Crypto BI\data_ingestion"
"C:\Users\user\Documents\Power BI Desktop\Projects\Crypto BI\.venv\Scripts\python.exe" etl.py >> "C:\Users\user\Documents\Power BI Desktop\Projects\Crypto BI\logs\etl_log.txt" 2>&1