@echo off
psql -U postgres -d crypto_analytics -p 5433 -f schema.sql
pause
