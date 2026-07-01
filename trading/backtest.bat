@echo off
REM ============================================================
REM  Quick backtest on the M15 timeframe (resampled from the M5
REM  export). Pure Volume Profile + filters, NO session lock.
REM  Partial take-profit + breakeven are ON by default.
REM  --walk-forward 5 gives an honest out-of-sample check.
REM  (For the full timeframe comparison + visual, run report.bat)
REM ============================================================
cd /d "%~dp0"
python run_backtest.py --csv "%~dp0data\XAUUSD_M5.csv" --resample M15 --walk-forward 5
pause
