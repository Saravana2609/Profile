"""Local paths and default run settings.

Edit GOLD_DIR if you move the project. On Windows this is where MT5 exports
and backtests read/write data.
"""

import os

# Your MT5 working folder (Windows). Data CSVs live in GOLD_DIR/data.
GOLD_DIR = r"C:\Users\Saravana_Rx100\Gold"

DATA_DIR = os.path.join(GOLD_DIR, "data")

# Default instrument / timeframe for fetching and backtesting.
SYMBOL = "XAUUSD"
TIMEFRAME = "M15"
BARS = 100_000


def default_csv() -> str:
    """Path of the default exported CSV for SYMBOL/TIMEFRAME."""
    return os.path.join(DATA_DIR, f"{SYMBOL}_{TIMEFRAME}.csv")
