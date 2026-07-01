# XAUUSD Volume Profile Strategy — Complete Implementation Plan

A self-contained blueprint for building, validating, and (optionally)
ML-enhancing a Volume-Profile reversal strategy on gold. Hand this to a fresh
session and it has everything needed to implement from scratch or extend the
existing `trading/` toolkit.

---

## 0. Honest expectations (read first)

- **No system predicts every tick.** The goal is a *positive statistical edge*
  after realistic costs, not certainty.
- **Realistic win rate: 55–65%** with disciplined filtering. Anything claiming
  "90%+ accuracy" is overfit or a scam.
- **Win rate is not profit.** Optimize **expectancy** = `Win% × AvgWin − Loss% ×
  AvgLoss`, plus profit factor and max drawdown. A 45% win rate at 2:1 R:R beats
  a 70% win rate at 0.3:1.
- **Gold has no true volume.** XAUUSD is OTC; profiles are built on broker tick
  volume (an approximation). Optionally cross-check against COMEX GC futures.
- **Backtest ≠ live.** Only trust results that survive **walk-forward,
  out-of-sample**, with spread/slippage charged. Then paper-trade before risking
  real money.

---

## 1. Objective

Fade price back toward fair value (POC) when it reaches the edge of the Value
Area **in a ranging market**, with confirmation, and manage the trade to lock in
a high-quality win rate without capping the edge.

---

## 2. Data layer

| Item | Spec |
|---|---|
| Symbol | XAUUSD (broker) — optionally GC futures for volume cross-check |
| Base timeframe to export | **M5** (resample everything higher from it) |
| History | ≥ 2–3 years (100k+ M5 bars) for meaningful walk-forward |
| Source | MT5 (`MetaTrader5` pkg, Windows) → CSV; or CSV from any broker |
| Fields | time, open, high, low, close, volume (tick volume for gold) |

**Rule:** export the lowest timeframe once; derive M15/M30/H1/H4 by resampling
so every comparison uses one consistent dataset.

---

## 3. Volume Profile engine

Build a **rolling** profile over the last `lookback` bars (default 200). Spread
each bar's volume across the price bins its high–low range covers.

Extract:
- **POC** (Point of Control): highest-volume price → reversion target / fair value
- **VAH / VAL**: edges of the Value Area holding **70%** of volume → entry zones
- **HVN / LVN**: local volume peaks/troughs → support-resistance / fast-move gaps

**Recompute per bar using only past bars** (no lookahead).

---

## 4. Timeframe framework (top-down)

| Role | Timeframe | Purpose |
|---|---|---|
| Context | **Daily / prior-day profile** | Where is value? Big POC/VAH/VAL levels |
| Execution | **M15–H1** (sweet spot) | Time the entry at those levels |
| Avoid | ≤ M5 (noise/spread), ≥ H4 (too few trades) | |

Let `analyze.py` rank timeframes by expectancy on *your* data — don't assume.
**Best practice: multi-timeframe confluence** — only take an M15 signal when it
aligns with the Daily value area.

---

## 5. Filters (the win-rate levers)

Apply in order; each removes low-quality trades:

1. **Regime filter (biggest lever).** Only fade levels when **ranging**
   (ADX < 25, or the ML regime model says range). In trends, stand aside or
   switch to breakout logic. Reversion into a trend is the #1 account killer.
2. **Level-quality filter.** Trade only Value-Area *edges* (VAH/VAL) and strong
   HVNs. Skip random prices. Do **not** fade an LVN (price slices through) —
   trade those as breakouts instead.
3. **Confirmation.** Require a **rejection candle** at the level (long: lower-wick
   > 50% of range + close up; short: mirror). Don't anticipate — react.
4. **Reward:risk floor.** Skip setups whose POC target gives < **1.2:1** R:R.
5. **Confluence bonus (optional).** Extra edge when the level coincides with a
   prior-day POC, round number, or higher-timeframe value-area edge.

> NOTE: No session lock by default. If you later find your broker's data is dead
> in the Asian session, add an optional hour filter — but prove it helps first.

---

## 6. Entry rules

**Long setup** (mirror for short at VAH):
1. Market is ranging (regime filter passes).
2. Current bar's low touches **VAL** (within `touch_atr × ATR`, default 0.25).
3. Bar closes back **inside** the value area (rejection).
4. Rejection candle confirmed.
5. Target = **POC**; entry = close; stop = `VAL − stop_atr × ATR` (default 0.75).
6. R:R ≥ `min_rr`. If all pass → **enter long on next bar**.

---

## 7. Trade management / exits

| Component | Rule | Effect |
|---|---|---|
| **Initial stop** | Beyond the level (`stop_atr × ATR`) | Defines 1R |
| **Partial TP** | Close **50%** at **+1R** | Locks profit, raises realized win rate |
| **Breakeven** | After partial, move stop to entry | Runner becomes risk-free |
| **Final target** | Remaining 50% to **POC** | Captures the reversion |
| **Time stop** | Exit after `max_hold_bars` (default 96 = 24h on M15) | Avoids dead trades |

> Trade-off to respect: partial TP **raises win rate but caps winners** —
> expectancy can fall. Test with and without (`--no-partial`) on real data.

---

## 8. Risk management (non-negotiable)

- **Risk per trade: 0.5–1% of account.** Never scale this up after wins.
- **Position size** = `(account × risk%) / (stop_distance × contract_value)`.
- **Daily loss limit:** stop trading after e.g. −3R in a day.
- **Correlation:** don't stack multiple gold-correlated positions as "separate" risk.
- **News:** skip fading levels right before high-impact events (NFP, CPI, FOMC) —
  gold gaps through everything.
- **Never auto-trade a live account until validated + paper-traded.**

---

## 9. Backtesting & validation methodology

1. **Cost model:** charge spread (~0.25 pt), slippage (~0.10 pt), commission on
   every trade. Non-negotiable — it separates real edges from fantasies.
2. **Full-sample backtest** → sanity check, not proof.
3. **Walk-forward (5+ sequential folds):** train/observe on past, test on the
   next unseen block. The aggregate out-of-sample expectancy is the real number.
4. **Metrics that matter:** expectancy (R), profit factor, max drawdown, Sharpe,
   trade count. Win rate is secondary.
5. **Robustness:** vary `lookback`, `adx_threshold`, `min_rr` ±20% — a real edge
   degrades gracefully, an overfit one collapses.
6. **Report:** timeframe ranking + Volume Profile + equity curve + daily/weekly
   P&L (see `analyze.py`).

**Red flags:** equity curve too smooth, one timeframe wildly better than
neighbours, edge vanishes when costs rise slightly → overfit / leakage.

---

## 10. ML roadmap (only after a rule-based edge exists)

Build ML **on top of** proven rules to *filter/score*, not to predict price.

- **Phase A — Regime classifier** (highest value, partly built as `RegimeModel`).
  Features: ADX, ATR%, efficiency ratio, MA-distance, return-std. Label: is the
  next N bars ranging? Use to gate entries.
- **Phase B — Setup-scoring model.** For each rule signal, features: distance to
  POC/VAH/VAL, HVN/LVN context, rejection strength, ATR, volatility state,
  multi-timeframe agreement. Label via **triple-barrier** (did +R or −R hit
  first?). Model: **LightGBM/XGBoost** (beats deep nets on tabular). Take only
  high-probability setups.
- **Phase C — Volatility-expansion model.** Predict P(big move soon) — the most
  statistically tractable target (volatility clusters). Use to time breakouts and
  avoid fading before expansion.
- **Validation:** **purged, embargoed walk-forward CV only.** Never random k-fold
  on time series. Leakage here is the #1 failure mode.

---

## 11. Implementation checklist

Existing `trading/` toolkit already covers 1–7. To build fresh or extend:

- [ ] Data loaders: MT5 / CSV / resample (`data.py`)
- [ ] Volume Profile engine: POC/VAH/VAL/HVN/LVN (`profile.py`)
- [ ] Regime filter: ADX rule + ML model (`regime.py`)
- [ ] Signal generation with filters (`strategy.py`)
- [ ] Backtester: costs, partial TP, breakeven, metrics (`backtest.py`)
- [ ] Timeframe analysis + HTML report with charts (`analyze.py`, `report.py`)
- [ ] Walk-forward evaluation (`run_backtest.py --walk-forward`)
- [ ] **NEXT:** rolling walk-forward panel in the report (edge stability)
- [ ] **NEXT:** setup-scoring ML model (Phase B) + triple-barrier labeling
- [ ] **NEXT:** multi-timeframe confluence feature (Daily ∧ M15)
- [ ] **NEXT:** paper-trading bridge (read signals → alert, no auto-execute)

---

## 12. Parameter reference (defaults)

| Param | Default | Meaning |
|---|---|---|
| `lookback` | 200 | Bars per rolling profile |
| `profile_bins` | 50 | Price bins in the profile |
| `value_area_pct` | 0.70 | Value Area coverage |
| `touch_atr` | 0.25 | How close to a level counts as a touch (× ATR) |
| `stop_atr` | 0.75 | Stop distance beyond level (× ATR) |
| `min_rr` | 1.2 | Minimum reward:risk to take a trade |
| `adx_threshold` | 25 | Below = ranging (fade); above = trending (skip) |
| `require_rejection` | True | Demand a rejection candle |
| `partial_tp_r` | 1.0 | Book partial at this R |
| `partial_fraction` | 0.5 | Fraction closed at partial |
| `max_hold_bars` | 96 | Time stop |
| `spread_usd` | 0.25 | XAUUSD spread charged per trade |
| risk per trade | 0.5–1% | Account risk per position |

---

## 13. Top pitfalls to avoid

1. **Lookahead/leakage** — only use past bars for the current decision.
2. **Ignoring costs** — always charge spread/slippage.
3. **Optimizing win rate** — optimize expectancy.
4. **Fading trends** — the regime filter exists for this reason.
5. **Overfitting** — few parameters, robustness-test, trust only walk-forward.
6. **Curve-fitting timeframes** — pick by out-of-sample expectancy, not the
   prettiest in-sample chart.
7. **Auto-trading unvalidated code on a live account** — paper-trade first.

---

*Research/education only. Not financial advice. Trading XAUUSD carries
substantial risk of loss.*
