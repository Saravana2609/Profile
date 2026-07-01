"""Export XAUUSD history from MT5 to a CSV.

RUN THIS ON YOUR OWN WINDOWS MACHINE with MetaTrader 5 installed and the
terminal open and logged in. It cannot run in a Linux/cloud environment
because MetaQuotes' `MetaTrader5` package is Windows-only and talks to the
local terminal.

    pip install MetaTrader5 pandas
    python fetch_mt5.py --symbol XAUUSD --timeframe M15 --bars 100000

The resulting CSV drops into ./data and is consumed by run_backtest.py:

    python run_backtest.py --csv data/XAUUSD_M15.csv
"""

from __future__ import annotations

import argparse
import os

from volume_profile.data import load_from_mt5


def main() -> None:
    p = argparse.ArgumentParser(description="Export XAUUSD bars from MT5 to CSV")
    p.add_argument("--symbol", default="XAUUSD")
    p.add_argument("--timeframe", default="M15",
                   choices=["M1", "M5", "M15", "M30", "H1", "H4", "D1"])
    p.add_argument("--bars", type=int, default=100_000)
    p.add_argument("--out", default=None)
    args = p.parse_args()

    df = load_from_mt5(args.symbol, args.timeframe, args.bars)
    os.makedirs("data", exist_ok=True)
    out = args.out or f"data/{args.symbol}_{args.timeframe}.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} bars to {out}")
    print(df.tail())


if __name__ == "__main__":
    main()
