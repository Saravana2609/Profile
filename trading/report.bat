@echo off
REM ============================================================
REM  Timeframe analysis + full daily/weekly HTML report.
REM  Pure Volume Profile + filters (regime/rejection/RR) — NO
REM  session lock. Compares M15/M30/H1/H4 resampled from the
REM  base export and opens the report in your browser.
REM
REM  Export the LOWEST timeframe first (edit fetch.bat to M5 for
REM  the richest comparison), then run this.
REM ============================================================
cd /d "%~dp0"
python analyze.py --csv "%~dp0data\XAUUSD_M5.csv" --base M5 --timeframes M15,M30,H1,H4 --out "%~dp0report.html"
echo.
echo Opening report...
start "" "%~dp0report.html"
pause
