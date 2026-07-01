@echo off
REM ============================================================
REM  One-time setup — installs Python dependencies incl. MT5.
REM  Run this once from C:\Users\Saravana_Rx100\Gold
REM ============================================================
cd /d "%~dp0"
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install MetaTrader5
echo.
echo Setup complete.
echo   1) Open MetaTrader 5 and log in.
echo   2) Double-click fetch.bat to export XAUUSD data.
echo   3) Double-click backtest.bat to run the strategy.
pause
