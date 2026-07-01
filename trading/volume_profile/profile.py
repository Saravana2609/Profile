"""Volume Profile engine.

Builds a volume-by-price histogram for a window of bars and extracts the
levels the strategy trades against:

- POC  (Point of Control): price bin with the most volume
- VAH / VAL: edges of the Value Area holding ``value_area_pct`` of volume
- HVN / LVN: local peaks / troughs of the volume-by-price curve

Gold (XAUUSD) has no true exchange volume, so this is built on broker tick
volume. Treat the levels as an approximation of where activity concentrated,
not exact traded size.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class VolumeProfile:
    poc: float
    vah: float
    val: float
    bin_prices: np.ndarray = field(repr=False)
    bin_volumes: np.ndarray = field(repr=False)
    hvn: list[float] = field(default_factory=list)
    lvn: list[float] = field(default_factory=list)

    def nearest_level(self, price: float) -> tuple[str, float, float]:
        """Return (name, level_price, distance) of the closest key level."""
        levels = {"POC": self.poc, "VAH": self.vah, "VAL": self.val}
        name, lvl = min(levels.items(), key=lambda kv: abs(kv[1] - price))
        return name, lvl, abs(lvl - price)


def build_profile(
    bars: pd.DataFrame,
    bins: int = 50,
    value_area_pct: float = 0.70,
) -> VolumeProfile:
    """Build a Volume Profile from a window of OHLCV bars.

    Each bar's volume is spread evenly across the price bins its high-low range
    touches (a standard approximation when tick-level prints aren't available).
    """
    if len(bars) == 0:
        raise ValueError("Cannot build a profile from zero bars")

    lo = float(bars["low"].min())
    hi = float(bars["high"].max())
    if hi <= lo:
        hi = lo + 1e-6

    edges = np.linspace(lo, hi, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    vol_by_bin = np.zeros(bins)

    highs = bars["high"].to_numpy()
    lows = bars["low"].to_numpy()
    vols = bars["volume"].to_numpy(dtype=float)

    for h, l, v in zip(highs, lows, vols):
        lo_idx = np.searchsorted(edges, l, side="right") - 1
        hi_idx = np.searchsorted(edges, h, side="right") - 1
        lo_idx = max(0, min(lo_idx, bins - 1))
        hi_idx = max(0, min(hi_idx, bins - 1))
        n = hi_idx - lo_idx + 1
        vol_by_bin[lo_idx : hi_idx + 1] += v / n  # spread bar volume across its range

    poc_idx = int(np.argmax(vol_by_bin))
    poc = float(centers[poc_idx])

    # Grow the Value Area outward from the POC until it holds value_area_pct.
    total = vol_by_bin.sum()
    target = total * value_area_pct
    included = vol_by_bin[poc_idx]
    lo_i = hi_i = poc_idx
    while included < target and (lo_i > 0 or hi_i < bins - 1):
        left = vol_by_bin[lo_i - 1] if lo_i > 0 else -1.0
        right = vol_by_bin[hi_i + 1] if hi_i < bins - 1 else -1.0
        if right >= left:
            hi_i += 1
            included += vol_by_bin[hi_i]
        else:
            lo_i -= 1
            included += vol_by_bin[lo_i]

    val = float(centers[lo_i])
    vah = float(centers[hi_i])

    hvn, lvn = _find_nodes(centers, vol_by_bin)

    return VolumeProfile(
        poc=poc,
        vah=vah,
        val=val,
        bin_prices=centers,
        bin_volumes=vol_by_bin,
        hvn=hvn,
        lvn=lvn,
    )


def _find_nodes(
    centers: np.ndarray, vols: np.ndarray, prominence_ratio: float = 0.15
) -> tuple[list[float], list[float]]:
    """Find High/Low Volume Nodes as local maxima/minima of the profile curve.

    A node must stand out from its neighbours by ``prominence_ratio`` of the
    peak volume to count, which filters out flat-noise wiggles.
    """
    hvn: list[float] = []
    lvn: list[float] = []
    if len(vols) < 3:
        return hvn, lvn
    peak = vols.max()
    thresh = peak * prominence_ratio
    for i in range(1, len(vols) - 1):
        left, mid, right = vols[i - 1], vols[i], vols[i + 1]
        if mid > left and mid > right and (mid - min(left, right)) > thresh:
            hvn.append(float(centers[i]))
        elif mid < left and mid < right and (max(left, right) - mid) > thresh:
            lvn.append(float(centers[i]))
    return hvn, lvn
