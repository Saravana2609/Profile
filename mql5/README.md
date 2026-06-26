# CandleEA — Candle-Momentum Expert Advisor (MQL5)

A MetaTrader 5 Expert Advisor that trades in the direction of the last
completed candle: a bullish close opens a buy, a bearish close opens a sell.
The previous candle's extreme becomes the protective stop and the take-profit
is placed at a fixed reward-to-risk multiple.

This is version 2 — a rewrite of a minimal candle-direction script into a
strategy with proper risk management, entry filters and trade management.

## Strategy

On each **newly closed bar**:

1. Look at the previous candle (`open`, `close`, `high`, `low`).
2. If the candle is **bullish** (`close > open`) → consider a **buy**.
   If **bearish** (`close < open`) → consider a **sell**.
3. Apply entry filters (trend, body size, spread, session).
4. Stop loss = previous candle's low (buy) / high (sell).
5. Take profit = entry ± (risk × `RRR`).

Only one position (from this EA) is held at a time — it no longer stacks a
new order on every candle.

## Inputs

| Group | Input | Default | Description |
|-------|-------|---------|-------------|
| General | `InpMagic` | 990026 | Magic number; EA only touches its own trades |
| | `InpRRR` | 2.0 | Reward : risk ratio for the take-profit |
| | `InpSlippage` | 20 | Max deviation in points |
| Sizing | `InpUseRiskSizing` | true | Size the lot from risk % of balance |
| | `InpRiskPercent` | 1.0 | Risk per trade as % of balance |
| | `InpFixedLot` | 0.10 | Fallback fixed lot (also used if sizing off) |
| Filters | `InpUseTrendFilter` | true | Only trade with the EMA trend |
| | `InpEmaPeriod` | 50 | Trend EMA period |
| | `InpMinBodyPoints` | 50 | Minimum candle body in points (0 = off) |
| | `InpMaxSpreadPoints` | 30 | Max allowed spread in points (0 = off) |
| Session | `InpUseSession` | false | Restrict to a server-time window |
| | `InpStartHour` / `InpEndHour` | 7 / 20 | Session window (supports overnight) |
| Management | `InpUseBreakEven` | true | Move SL to break-even at `InpBreakEvenRR` |
| | `InpBreakEvenRR` | 1.0 | R multiple that triggers break-even |
| | `InpUseTrailing` | false | Enable trailing stop |
| | `InpTrailPoints` | 200 | Trailing distance in points |

## Improvements over the original script

- **Acts once per bar, reliably** — new-bar detection via the bar's open time
  instead of a flag that was only updated when a trade fired.
- **No order stacking** — checks for an existing position before entering.
- **Magic number** so it ignores manual/other-EA trades.
- **Risk-based position sizing** computed from the actual stop distance, with a
  safe fixed-lot fallback when tick value/size is unavailable.
- **Broker-safe SL/TP** — prices normalized to tick size and digits, and the
  `SYMBOL_TRADE_STOPS_LEVEL` minimum distance is enforced to avoid rejections.
- **Entry filters** — EMA trend, minimum candle body, spread cap, optional
  trading session.
- **Trade management** — optional break-even and trailing stop.

## Installation

1. Copy `CandleEA.mq5` into your terminal's
   `MQL5/Experts/` folder
   (in MetaEditor: *File → Open Data Folder → MQL5 → Experts*).
2. Compile in MetaEditor (F7).
3. Attach to a chart and enable **Algo Trading**.

> **Disclaimer:** For educational/testing purposes. Always backtest and
> forward-test on a demo account before risking real capital. Trading carries
> significant risk of loss.
