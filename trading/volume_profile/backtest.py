"""Event-driven backtester with realistic XAUUSD trading costs.

Each signal is simulated forward bar by bar until stop or target is hit (or a
time-stop). Spread, slippage and commission are charged on every trade, because
without them a Volume-Profile edge on gold looks far better than it really is.

Win-rate management (optional, on by default):
  - Partial take-profit: close ``partial_fraction`` of the position at
    ``partial_tp_r`` R, then move the stop to breakeven. A trade that reaches
    +1R and then reverses becomes a small win / scratch instead of a full loss,
    which lifts realized win rate and smooths the equity curve.

Reported metrics deliberately lead with expectancy, R-multiples and drawdown,
NOT win rate alone — a high win rate with poor R:R still loses money.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .strategy import Signal


@dataclass
class CostModel:
    spread_usd: float = 0.25       # XAUUSD spread in price points (~25 cents)
    slippage_usd: float = 0.10     # extra slippage per fill
    commission_usd: float = 0.0    # per-trade commission in price points
    max_hold_bars: int = 96        # time-stop (96 * M15 = 24h)
    # --- win-rate management ---
    enable_partial: bool = True    # scale out + move to breakeven
    partial_tp_r: float = 1.0      # book partial profit at this R multiple
    partial_fraction: float = 0.5  # fraction of position closed at partial TP
    move_to_breakeven: bool = True # after partial, trail stop to entry


@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    direction: int
    entry: float
    exit: float
    stop: float
    target: float
    r_multiple: float
    pnl: float
    outcome: str  # "target", "stop", "partial+be", "partial+target", "time"
    level_name: str


def run_backtest(
    bars: pd.DataFrame, signals: list[Signal], costs: CostModel | None = None
) -> tuple[list[Trade], dict]:
    costs = costs or CostModel()
    half_spread = costs.spread_usd / 2 + costs.slippage_usd
    trades: list[Trade] = []

    highs = bars["high"].to_numpy()
    lows = bars["low"].to_numpy()
    closes = bars["close"].to_numpy()
    times = bars["time"].to_numpy()
    n = len(bars)

    for sig in signals:
        d = sig.direction
        entry = sig.entry + d * half_spread          # pay spread/slippage on entry
        risk = abs(entry - sig.stop)
        if risk <= 0:
            continue

        stop = sig.stop
        partial_level = entry + d * costs.partial_tp_r * risk
        remaining = 1.0
        booked_pnl = 0.0        # realized price-P&L from the partial exit
        partial_done = False
        outcome = "time"
        exit_i = None
        final_exit_fill = None

        last = min(sig.idx + 1 + costs.max_hold_bars, n)
        for j in range(sig.idx + 1, last):
            hi, lo = highs[j], lows[j]

            # 1) Stop first (conservative: assume the adverse fill within the bar).
            hit_stop = lo <= stop if d > 0 else hi >= stop
            if hit_stop:
                exit_fill = stop - d * half_spread
                booked_pnl += remaining * d * (exit_fill - entry)
                exit_i = j
                final_exit_fill = exit_fill
                outcome = "partial+be" if partial_done else "stop"
                remaining = 0.0
                break

            # 2) Partial take-profit + move to breakeven.
            if costs.enable_partial and not partial_done:
                hit_partial = hi >= partial_level if d > 0 else lo <= partial_level
                if hit_partial:
                    exit_fill = partial_level - d * half_spread
                    booked_pnl += costs.partial_fraction * d * (exit_fill - entry)
                    remaining -= costs.partial_fraction
                    partial_done = True
                    if costs.move_to_breakeven:
                        stop = entry  # risk-free runner

            # 3) Final target (POC).
            hit_target = hi >= sig.target if d > 0 else lo <= sig.target
            if hit_target:
                exit_fill = sig.target - d * half_spread
                booked_pnl += remaining * d * (exit_fill - entry)
                exit_i = j
                final_exit_fill = exit_fill
                outcome = "partial+target" if partial_done else "target"
                remaining = 0.0
                break

        if remaining > 0:  # time-stop: close the rest at last close
            exit_i = min(sig.idx + costs.max_hold_bars, n - 1)
            exit_fill = closes[exit_i] - d * half_spread
            booked_pnl += remaining * d * (exit_fill - entry)
            final_exit_fill = exit_fill
            outcome = "partial+be" if partial_done else "time"

        pnl = booked_pnl - costs.commission_usd
        r_multiple = pnl / risk

        trades.append(
            Trade(
                entry_time=pd.Timestamp(times[sig.idx]),
                exit_time=pd.Timestamp(times[exit_i]),
                direction=d,
                entry=float(entry),
                exit=float(final_exit_fill),
                stop=float(sig.stop),
                target=float(sig.target),
                r_multiple=float(r_multiple),
                pnl=float(pnl),
                outcome=outcome,
                level_name=sig.level_name,
            )
        )

    return trades, _metrics(trades)


def _metrics(trades: list[Trade]) -> dict:
    if not trades:
        return {"trades": 0, "note": "No trades generated for these settings."}

    r = np.array([t.r_multiple for t in trades])
    wins = r[r > 0]
    losses = r[r <= 0]
    win_rate = len(wins) / len(r)

    gross_win = wins.sum()
    gross_loss = -losses.sum()
    profit_factor = gross_win / gross_loss if gross_loss > 0 else float("inf")

    equity = np.cumsum(r)  # equity curve in R units
    peak = np.maximum.accumulate(equity)
    max_dd = float((peak - equity).max()) if len(equity) else 0.0

    sharpe = float(r.mean() / r.std()) if r.std() > 0 else 0.0

    return {
        "trades": len(trades),
        "win_rate": round(win_rate, 4),
        "expectancy_R": round(float(r.mean()), 4),
        "avg_win_R": round(float(wins.mean()), 3) if len(wins) else 0.0,
        "avg_loss_R": round(float(losses.mean()), 3) if len(losses) else 0.0,
        "profit_factor": round(profit_factor, 3),
        "total_R": round(float(r.sum()), 2),
        "max_drawdown_R": round(max_dd, 2),
        "sharpe_per_trade": round(sharpe, 3),
        "target_hits": sum(t.outcome in ("target", "partial+target") for t in trades),
        "stop_hits": sum(t.outcome == "stop" for t in trades),
        "breakeven_exits": sum(t.outcome == "partial+be" for t in trades),
        "time_stops": sum(t.outcome == "time" for t in trades),
    }
