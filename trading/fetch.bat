@echo off
REM ============================================================
REM  Export XAUUSD history from MT5 to Gold\data\XAUUSD_M15.csv
REM  MetaTrader 5 must be OPEN and logged in first.
REM ============================================================
cd /d "%~dp0"
REM Export M5 as the base — higher timeframes are resampled from it.
python fetch_mt5.py --symbol XAUUSD --timeframe M5 --bars 100000
echo.
echo If you saw an MT5 error, make sure MetaTrader 5 is open and logged in.
pause
