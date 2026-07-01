@echo off
REM ============================================================
REM  Run the Volume-Profile strategy on the exported data,
REM  tuned for higher win rate:
REM    --session   trade only active (London/NY) hours
REM    (partial take-profit + breakeven are ON by default)
REM    --walk-forward 5  honest out-of-sample check
REM ============================================================
cd /d "%~dp0"
python run_backtest.py --csv "%~dp0data\XAUUSD_M15.csv" --session --walk-forward 5
pause
