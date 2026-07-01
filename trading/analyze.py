"""Timeframe analysis + full daily/weekly report with visuals.

Runs the Volume-Profile strategy (regime + rejection + reward:risk filters —
NO session lock) across several timeframes, ranks them by expectancy, then
writes a self-contained HTML report for the best one.

Usage:
    python analyze.py                      # synthetic demo (runs anywhere)
    python analyze.py --csv data/XAUUSD_M5.csv
    python analyze.py --csv data/XAUUSD_M5.csv --timeframes M15,M30,H1,H4
    python analyze.py --mt5 --base M5

Give it the LOWEST timeframe you have; higher ones are resampled from it so the
comparison uses one consistent dataset.
"""

from __future__ import annotations

import argparse
import os

from volume_profile import (
    CostModel,
    StrategyConfig,
    build_profile,
    generate_signals,
    generate_synthetic,
    load_from_csv,
    load_from_mt5,
    run_backtest,
)
from volume_profile.data import resample_ohlcv
from volume_profile.report import (
    build_html_report,
    daily_table,
    plot_equity,
    plot_period_pnl,
    plot_timeframe_comparison,
    plot_volume_profile,
    weekly_table,
)

# Timeframe -> minutes.
TF_MINUTES = {"M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}


def analyze_timeframe(base_bars, minutes: int, cfg: StrategyConfig, costs: CostModel):
    bars = resample_ohlcv(base_bars, minutes) if minutes else base_bars
    if len(bars) <= cfg.lookback + 20:
        return None
    signals = generate_signals(bars, cfg)
    trades, metrics = run_backtest(bars, signals, costs)
    return {"bars": bars, "signals": signals, "trades": trades, "metrics": metrics}


def pick_best(results: list[dict], min_trades: int = 15) -> dict:
    """Best = highest expectancy among timeframes with enough trades.

    Falls back to the most-traded timeframe if none clear the trade minimum.
    """
    eligible = [r for r in results if r["metrics"].get("trades", 0) >= min_trades]
    pool = eligible or results
    return max(pool, key=lambda r: r["metrics"].get("expectancy_R", -99))


def main() -> None:
    p = argparse.ArgumentParser()
    src = p.add_mutually_exclusive_group()
    src.add_argument("--csv", help="Lowest-timeframe OHLCV CSV (from fetch_mt5.py)")
    src.add_argument("--mt5", action="store_true", help="Pull from MT5 (Windows)")
    p.add_argument("--symbol", default="XAUUSD")
    p.add_argument("--base", default="M5", help="Timeframe of the source data")
    p.add_argument("--timeframes", default="M15,M30,H1,H4",
                   help="Comma list to compare (resampled from base)")
    p.add_argument("--lookback", type=int, default=200)
    p.add_argument("--min-rr", type=float, default=1.2)
    p.add_argument("--adx", type=float, default=25.0)
    p.add_argument("--no-regime", action="store_true")
    p.add_argument("--out", default="report.html")
    args = p.parse_args()

    is_synth = False
    if args.csv:
        print(f"Loading {args.csv} ...")
        base_bars = load_from_csv(args.csv)
    elif args.mt5:
        print(f"Pulling {args.symbol} {args.base} from MT5 ...")
        base_bars = load_from_mt5(args.symbol, args.base, 100_000)
    else:
        print("No data source — generating synthetic M5-like data.")
        base_bars = generate_synthetic(bars=40_000, timeframe_minutes=5)
        is_synth = True

    print(f"Base: {len(base_bars):,} bars "
          f"({base_bars['time'].iloc[0]} -> {base_bars['time'].iloc[-1]})")

    cfg = StrategyConfig(
        lookback=args.lookback,
        min_rr=args.min_rr,
        adx_threshold=args.adx,
        use_regime_filter=not args.no_regime,
        session_filter=False,  # explicitly NO session lock — pure VP + filters
    )
    costs = CostModel()

    tfs = [t.strip().upper() for t in args.timeframes.split(",") if t.strip()]
    results = []
    print("\nTimeframe comparison (expectancy-ranked):")
    print(f"{'TF':>5} {'trades':>7} {'win%':>7} {'expR':>8} {'PF':>6} {'totR':>8}")
    for tf in tfs:
        if tf not in TF_MINUTES:
            print(f"  skip {tf}: unknown timeframe")
            continue
        res = analyze_timeframe(base_bars, TF_MINUTES[tf], cfg, costs)
        if res is None:
            print(f"  skip {tf}: not enough bars")
            continue
        res["timeframe"] = tf
        m = res["metrics"]
        results.append(res)
        print(f"{tf:>5} {m.get('trades', 0):>7} "
              f"{m.get('win_rate', 0) * 100:>6.1f}% {m.get('expectancy_R', 0):>+8.3f} "
              f"{m.get('profit_factor', 0):>6} {m.get('total_R', 0):>+8.1f}")

    if not results:
        print("\nNo timeframe produced trades. Loosen filters or supply more data.")
        return

    best = pick_best(results)
    print(f"\n🏆 Best timeframe by expectancy: {best['timeframe']} "
          f"({best['metrics'].get('expectancy_R', 0):+.3f} R/trade)")

    # Build visuals for the best timeframe.
    bb = best["bars"]
    window = bb.iloc[-cfg.lookback:]
    vp = build_profile(window, bins=cfg.profile_bins, value_area_pct=cfg.value_area_pct)

    vp_img = plot_volume_profile(window, vp, f"{args.symbol} {best['timeframe']} — latest profile")
    equity_img = plot_equity(best["trades"], f"Equity — {best['timeframe']}")
    tf_img = plot_timeframe_comparison(results)
    period_img = plot_period_pnl(best["trades"])
    daily = daily_table(best["trades"])
    weekly = weekly_table(best["trades"])

    html = build_html_report(
        symbol=args.symbol,
        results=results,
        best=best,
        vp_img=vp_img,
        equity_img=equity_img,
        tf_img=tf_img,
        period_img=period_img,
        daily=daily,
        weekly=weekly,
        generated=str(base_bars["time"].iloc[-1]),
        is_synthetic=is_synth,
    )
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nReport written to {os.path.abspath(args.out)}")
    print("Open it in a browser to see the full visual report.")


if __name__ == "__main__":
    main()
