# XAUUSD Volume Profile — Backtesting Toolkit

A backtesting system for a **Volume Profile reversal strategy** on gold
(XAUUSD), with a trend-vs-range regime filter and realistic trading costs.

It runs anywhere on synthetic data (to validate the logic) and on **real MT5
data** exported from your own Windows machine.

> ⚠️ **Honest expectations.** No system predicts every tick. This tool measures
> whether a Volume-Profile edge survives *realistic costs* on *out-of-sample*
> data. It leads with **expectancy and drawdown**, not win rate — a high win
> rate with poor risk/reward still loses money. Judge real edge only on real
> XAUUSD data, validated walk-forward. Treat any "90%+ accuracy" claim as a red
> flag.

## Why the two-machine split

MetaQuotes' `MetaTrader5` Python package is **Windows-only** and talks to a
running MT5 terminal on the same machine. So:

- **On your Windows PC (with MT5 open):** run `fetch_mt5.py` to export a CSV.
- **Anywhere (PC, Mac, Linux, cloud):** run `run_backtest.py` on that CSV.

The strategy/backtest code is identical regardless of data source.

## Quick start

### 1. Install
```bash
pip install -r requirements.txt
# On Windows also: pip install MetaTrader5
```

### 2. See it run immediately (synthetic data, no MT5 needed)
```bash
python run_backtest.py --walk-forward 5
```
This proves the pipeline works. The numbers are meaningless for real trading —
synthetic data has no real edge by design.

### 3. Get real data from MT5 (on your Windows machine)
Open MT5, log in, then:
```bash
python fetch_mt5.py --symbol XAUUSD --timeframe M15 --bars 100000
```
Writes `data/XAUUSD_M15.csv`.

### 4. Backtest on the real data
```bash
python run_backtest.py --csv data/XAUUSD_M15.csv --walk-forward 5
```

## Key options
```
--csv PATH           Use an exported CSV (recommended)
--mt5                Pull live from MT5 (Windows only)
--timeframe M15      M1/M5/M15/M30/H1/H4/D1  (Daily context + M15/H1 execution recommended)
--lookback 200       Bars per rolling Volume Profile
--min-rr 1.2         Skip setups below this reward:risk
--adx 25             Trend threshold; below = ranging (safe to fade)
--no-regime          Disable the trend/range filter (usually hurts win rate)
--spread 0.25        XAUUSD spread in price points charged per trade
--walk-forward N     Evaluate on N sequential out-of-sample folds
```

## How the strategy works

1. **Volume Profile** (`profile.py`) — rolling POC / VAH / VAL / HVN / LVN.
2. **Regime filter** (`regime.py`) — only fade levels when the market is
   *ranging* (ADX rule by default; an optional ML classifier is included).
3. **Signals** (`strategy.py`) — at the Value-Area edge, in a ranging market,
   with a rejection candle and a minimum reward:risk, fade toward the POC.
4. **Backtest** (`backtest.py`) — simulate each trade forward with spread,
   slippage and commission; report expectancy, profit factor, Sharpe, drawdown.

## The levers that raise win rate (~50% → ~60%+)

Each is a config knob so you can measure its effect honestly:

- **Regime filter** — the single biggest lever (`--adx`, `use_regime_filter`).
- **Trade-quality filter** — only the Value-Area edges, not every level.
- **Confirmation** — `require_rejection` (rejection candle before entry).
- **Reward:risk floor** — `--min-rr`.

## Roadmap (not yet built)

- ML setup-scoring model on top of the rule signals (`RegimeModel` is the seed).
- Session-anchored profiles (Asia / London / NY) — gold is session-driven.
- Multi-timeframe confluence (Daily value area agreeing with H1).
- Reversal-probability and volatility-expansion classifiers.

## Files
```
volume_profile/
  data.py       MT5 / CSV / synthetic data loaders
  profile.py    Volume Profile engine (POC/VAH/VAL/HVN/LVN)
  regime.py     Trend-vs-range filter (ADX rule + optional ML model)
  strategy.py   Reversal signal generation
  backtest.py   Event-driven backtester + metrics
fetch_mt5.py    Export MT5 history to CSV (Windows)
run_backtest.py Main entry point
```

**This is a research/education tool, not financial advice. Trading XAUUSD
carries substantial risk of loss.**
