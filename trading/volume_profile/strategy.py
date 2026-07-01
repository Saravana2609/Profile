"""Volume-Profile reversal strategy with a regime filter and confirmation.

Core idea (the setup we discussed):
  - Build a Volume Profile over a rolling lookback window.
  - When price reaches the Value-Area edge (VAL from below / VAH from above)
    AND the market is ranging AND price shows a rejection candle,
    fade back toward the POC.
  - Stop beyond the level; target the POC (with an R-multiple floor).

Every filter here exists to raise trade quality (win rate) by taking fewer,
better trades — exactly the levers that move a ~50% system toward ~60%+.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .profile import build_profile
from .regime import adx_regime, atr


@dataclass
class Signal:
    idx: int
    time: pd.Timestamp
    direction: int  # +1 long, -1 short
    entry: float
    stop: float
    target: float
    level_name: str
    level_price: float


@dataclass
class StrategyConfig:
    lookback: int = 200          # bars used to build each rolling profile
    profile_bins: int = 50
    value_area_pct: float = 0.70
    touch_atr: float = 0.25      # how close to a level counts as a "touch" (in ATR)
    stop_atr: float = 0.75       # stop distance beyond the level (in ATR)
    min_rr: float = 1.2          # skip setups whose POC target is < this R:R
    use_regime_filter: bool = True
    adx_threshold: float = 25.0
    require_rejection: bool = True


def _is_rejection(bar, direction: int) -> bool:
    """Long: lower-wick rejection. Short: upper-wick rejection."""
    rng = bar["high"] - bar["low"]
    if rng <= 0:
        return False
    body_lo = min(bar["open"], bar["close"])
    body_hi = max(bar["open"], bar["close"])
    lower_wick = body_lo - bar["low"]
    upper_wick = bar["high"] - body_hi
    if direction > 0:
        return lower_wick > 0.5 * rng and bar["close"] > bar["open"]
    return upper_wick > 0.5 * rng and bar["close"] < bar["open"]


def generate_signals(bars: pd.DataFrame, cfg: StrategyConfig | None = None) -> list[Signal]:
    """Walk the series bar by bar and emit reversal signals.

    Only past bars are ever used to build the profile for the current bar, so
    the signal generation is free of lookahead.
    """
    cfg = cfg or StrategyConfig()
    atr_series = atr(bars).to_numpy()
    ranging = (
        adx_regime(bars, cfg.adx_threshold).to_numpy()
        if cfg.use_regime_filter
        else None
    )

    signals: list[Signal] = []
    for i in range(cfg.lookback, len(bars)):
        a = atr_series[i]
        if not (a and a > 0):
            continue
        if ranging is not None and not ranging[i]:
            continue  # only fade levels when ranging

        window = bars.iloc[i - cfg.lookback : i]
        vp = build_profile(window, bins=cfg.profile_bins, value_area_pct=cfg.value_area_pct)
        bar = bars.iloc[i]
        price = bar["close"]
        touch = cfg.touch_atr * a

        direction = 0
        level_name = ""
        level_price = 0.0
        # Long from the lower Value-Area edge; short from the upper edge.
        if abs(bar["low"] - vp.val) <= touch and price > vp.val - touch:
            direction, level_name, level_price = 1, "VAL", vp.val
        elif abs(bar["high"] - vp.vah) <= touch and price < vp.vah + touch:
            direction, level_name, level_price = -1, "VAH", vp.vah
        else:
            continue

        if cfg.require_rejection and not _is_rejection(bar, direction):
            continue

        entry = price
        stop = level_price - cfg.stop_atr * a if direction > 0 else level_price + cfg.stop_atr * a
        target = vp.poc  # reversion target is the Point of Control

        risk = abs(entry - stop)
        reward = abs(target - entry)
        if risk <= 0 or reward / risk < cfg.min_rr:
            continue
        # Target must sit on the profit side of entry.
        if (direction > 0 and target <= entry) or (direction < 0 and target >= entry):
            continue

        signals.append(
            Signal(
                idx=i,
                time=bar["time"],
                direction=direction,
                entry=float(entry),
                stop=float(stop),
                target=float(target),
                level_name=level_name,
                level_price=float(level_price),
            )
        )
    return signals
