"""Run the Volume-Profile reversal backtest.

Data source, in order of preference:
  --csv PATH   : a CSV exported from MT5 (see fetch_mt5.py) or any broker
  --mt5        : pull live from a running MT5 terminal (Windows only)
  (default)    : synthetic gold-like data, so the pipeline runs anywhere

Examples:
    python run_backtest.py                          # synthetic demo
    python run_backtest.py --csv data/XAUUSD_M15.csv
    python run_backtest.py --mt5 --timeframe M15 --bars 100000
    python run_backtest.py --csv data/XAUUSD_M15.csv --walk-forward 5
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

from volume_profile import (
    CostModel,
    StrategyConfig,
    generate_signals,
    generate_synthetic,
    load_from_csv,
    load_from_mt5,
    run_backtest,
)


def _print_metrics(title: str, metrics: dict) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(metrics, indent=2, default=str))


def _interpret(metrics: dict) -> None:
    if metrics.get("trades", 0) == 0:
        print("\nNo trades — loosen touch_atr / lower min_rr, or check the data.")
        return
    exp = metrics["expectancy_R"]
    wr = metrics["win_rate"]
    print("\n--- Reading the result ---")
    print(f"Win rate     : {wr:.1%}")
    print(f"Expectancy   : {exp:+.3f} R per trade  (>0 means a positive edge)")
    print(f"Profit factor: {metrics['profit_factor']}")
    if exp > 0:
        print("Positive expectancy on THIS data. Validate on real MT5 data and "
              "out-of-sample before trusting it.")
    else:
        print("Negative expectancy here — the raw edge isn't there yet. This is "
              "the normal starting point; tune filters and re-test honestly.")
    print("NOTE: On synthetic data these numbers only prove the pipeline runs. "
          "Real edge can only be judged on real XAUUSD data.")


def walk_forward(bars: pd.DataFrame, cfg: StrategyConfig, costs: CostModel, folds: int) -> None:
    """Evaluate on sequential out-of-sample folds (no shuffling of time)."""
    print(f"\n########## WALK-FORWARD ({folds} sequential folds) ##########")
    size = len(bars) // folds
    all_r: list[float] = []
    for f in range(folds):
        seg = bars.iloc[f * size : (f + 1) * size].reset_index(drop=True)
        if len(seg) <= cfg.lookback + 10:
            continue
        sigs = generate_signals(seg, cfg)
        trades, metrics = run_backtest(seg, sigs, costs)
        all_r += [t.r_multiple for t in trades]
        wr = metrics.get("win_rate", 0)
        exp = metrics.get("expectancy_R", 0)
        print(f"Fold {f + 1}: trades={metrics.get('trades', 0):4d}  "
              f"win_rate={wr:.1%}  expectancy={exp:+.3f}R  "
              f"total={metrics.get('total_R', 0):+.1f}R")
    if all_r:
        r = np.array(all_r)
        print(f"\nAggregate OOS: trades={len(r)}  win_rate={(r > 0).mean():.1%}  "
              f"expectancy={r.mean():+.3f}R  total={r.sum():+.1f}R")


def main() -> None:
    p = argparse.ArgumentParser()
    src = p.add_mutually_exclusive_group()
    src.add_argument("--csv", help="Path to an OHLCV CSV (from fetch_mt5.py)")
    src.add_argument("--mt5", action="store_true", help="Pull live from MT5 (Windows)")
    p.add_argument("--symbol", default="XAUUSD")
    p.add_argument("--timeframe", default="M15")
    p.add_argument("--bars", type=int, default=20_000)
    p.add_argument("--lookback", type=int, default=200)
    p.add_argument("--min-rr", type=float, default=1.2)
    p.add_argument("--adx", type=float, default=25.0)
    p.add_argument("--no-regime", action="store_true", help="Disable the regime filter")
    p.add_argument("--spread", type=float, default=0.25, help="XAUUSD spread in points")
    p.add_argument("--walk-forward", type=int, default=0, metavar="N",
                   help="Run N sequential out-of-sample folds")
    args = p.parse_args()

    if args.csv:
        print(f"Loading {args.csv} ...")
        bars = load_from_csv(args.csv)
    elif args.mt5:
        print(f"Pulling {args.symbol} {args.timeframe} from MT5 ...")
        bars = load_from_mt5(args.symbol, args.timeframe, args.bars)
    else:
        print("No data source given — generating synthetic gold-like data.")
        print("(Use --csv data/XAUUSD_M15.csv for real MT5 data.)")
        bars = generate_synthetic(bars=args.bars)

    print(f"Loaded {len(bars):,} bars "
          f"({bars['time'].iloc[0]} -> {bars['time'].iloc[-1]})")

    cfg = StrategyConfig(
        lookback=args.lookback,
        min_rr=args.min_rr,
        adx_threshold=args.adx,
        use_regime_filter=not args.no_regime,
    )
    costs = CostModel(spread_usd=args.spread)

    signals = generate_signals(bars, cfg)
    print(f"Generated {len(signals)} signals")
    trades, metrics = run_backtest(bars, signals, costs)
    _print_metrics("FULL-SAMPLE BACKTEST", metrics)
    _interpret(metrics)

    if args.walk_forward:
        walk_forward(bars, cfg, costs, args.walk_forward)


if __name__ == "__main__":
    main()
