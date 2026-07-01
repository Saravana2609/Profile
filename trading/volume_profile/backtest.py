"""Event-driven backtester with realistic XAUUSD trading costs.

Each signal is simulated forward bar by bar until stop or target is hit (or a
time-stop). Spread, slippage and commission are charged on every trade, because
without them a Volume-Profile edge on gold looks far better than it really is.

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
    outcome: str  # "target", "stop", "time"
    level_name: str


def run_backtest(
    bars: pd.DataFrame, signals: list[Signal], costs: CostModel | None = None
) -> tuple[list[Trade], dict]:
    costs = costs or CostModel()
    half_spread = costs.spread_usd / 2 + costs.slippage_usd
    trades: list[Trade] = []

    highs = bars["high"].to_numpy()
    lows = bars["low"].to_numpy()
    times = bars["time"].to_numpy()
    n = len(bars)

    for sig in signals:
        # Enter on the next bar's open side, charging half-spread + slippage.
        entry = sig.entry + sig.direction * half_spread
        risk = abs(entry - sig.stop)
        if risk <= 0:
            continue

        exit_price = None
        exit_i = None
        outcome = "time"
        for j in range(sig.idx + 1, min(sig.idx + 1 + costs.max_hold_bars, n)):
            hi, lo = highs[j], lows[j]
            if sig.direction > 0:
                # Stop checked first (conservative: assume the worse fill).
                if lo <= sig.stop:
                    exit_price, exit_i, outcome = sig.stop, j, "stop"
                    break
                if hi >= sig.target:
                    exit_price, exit_i, outcome = sig.target, j, "target"
                    break
            else:
                if hi >= sig.stop:
                    exit_price, exit_i, outcome = sig.stop, j, "stop"
                    break
                if lo <= sig.target:
                    exit_price, exit_i, outcome = sig.target, j, "target"
                    break
        if exit_price is None:  # time-stop at last available bar
            exit_i = min(sig.idx + costs.max_hold_bars, n - 1)
            exit_price = bars["close"].to_numpy()[exit_i]

        # Charge exit-side costs too.
        exit_fill = exit_price - sig.direction * half_spread
        pnl = sig.direction * (exit_fill - entry) - costs.commission_usd
        r_multiple = pnl / risk

        trades.append(
            Trade(
                entry_time=pd.Timestamp(times[sig.idx]),
                exit_time=pd.Timestamp(times[exit_i]),
                direction=sig.direction,
                entry=float(entry),
                exit=float(exit_fill),
                stop=sig.stop,
                target=sig.target,
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

    # Per-trade Sharpe-like ratio on R-multiples (not annualised).
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
        "target_hits": sum(t.outcome == "target" for t in trades),
        "stop_hits": sum(t.outcome == "stop" for t in trades),
        "time_stops": sum(t.outcome == "time" for t in trades),
    }
