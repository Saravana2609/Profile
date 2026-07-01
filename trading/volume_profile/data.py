"""Data layer: load XAUUSD OHLCV bars from MT5, a CSV export, or a synthetic
generator.

MT5's Python API only runs on Windows with the terminal open, so the MT5 path
is import-guarded. On any platform you can load a CSV export or generate
synthetic gold-like data, which lets the whole pipeline be validated anywhere.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Canonical column names used everywhere downstream.
COLUMNS = ["time", "open", "high", "low", "close", "volume"]


def load_from_mt5(
    symbol: str = "XAUUSD",
    timeframe: str = "M15",
    bars: int = 50_000,
) -> pd.DataFrame:
    """Pull bars directly from a running MT5 terminal.

    Only works on Windows with MetaTrader5 installed and the terminal open.
    Run this on your own machine (see ``fetch_mt5.py``), export to CSV, then
    load the CSV anywhere with :func:`load_from_csv`.
    """
    try:
        import MetaTrader5 as mt5
    except ImportError as exc:  # pragma: no cover - platform specific
        raise RuntimeError(
            "MetaTrader5 package not available. It only runs on Windows with "
            "the MT5 terminal installed. Use fetch_mt5.py on your machine to "
            "export a CSV, then load that with load_from_csv()."
        ) from exc

    tf_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
    }
    if timeframe not in tf_map:
        raise ValueError(f"Unsupported timeframe {timeframe!r}. Choose from {list(tf_map)}")

    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize() failed: {mt5.last_error()}")
    try:
        rates = mt5.copy_rates_from_pos(symbol, tf_map[timeframe], 0, bars)
    finally:
        mt5.shutdown()

    if rates is None or len(rates) == 0:
        raise RuntimeError(f"No data returned for {symbol} {timeframe}")

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    # MT5 exposes tick volume as 'tick_volume'; gold has no true exchange volume.
    df = df.rename(columns={"tick_volume": "volume"})
    return df[COLUMNS].reset_index(drop=True)


def load_from_csv(path: str) -> pd.DataFrame:
    """Load bars from a CSV. Accepts common MT5/broker export headings."""
    df = pd.read_csv(path)
    df = df.rename(columns={c: c.lower().strip() for c in df.columns})
    rename = {
        "date": "time",
        "datetime": "time",
        "timestamp": "time",
        "tick_volume": "volume",
        "vol": "volume",
        "<date>": "time",
        "<open>": "open",
        "<high>": "high",
        "<low>": "low",
        "<close>": "close",
        "<tickvol>": "volume",
        "<vol>": "volume",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if "volume" not in df.columns:
        df["volume"] = 1.0  # fall back to flat volume if the export lacks it
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")
    df["time"] = pd.to_datetime(df["time"])
    return df[COLUMNS].sort_values("time").reset_index(drop=True)


def resample_ohlcv(bars: pd.DataFrame, minutes: int) -> pd.DataFrame:
    """Resample bars to a higher timeframe (e.g. M5 -> H1).

    Lets you export one low timeframe from MT5 and analyse every higher
    timeframe from it, so the timeframe comparison uses one consistent dataset.
    """
    df = bars.set_index("time")
    rule = f"{minutes}min"
    agg = df.resample(rule, label="left", closed="left").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    )
    return agg.dropna().reset_index()


def generate_synthetic(
    bars: int = 20_000,
    timeframe_minutes: int = 15,
    seed: int = 42,
    start_price: float = 2000.0,
) -> pd.DataFrame:
    """Generate gold-like OHLCV bars for validating the pipeline offline.

    The series deliberately mixes trending and ranging regimes with volatility
    clustering, so the regime filter and Volume Profile levels have something
    realistic to bite on. This is NOT real market data — use it only to prove
    the code runs, never to judge a strategy's real edge.
    """
    rng = np.random.default_rng(seed)

    # A slowly switching regime state drives drift and volatility, producing
    # alternating trend/range stretches with volatility clustering.
    regime = np.zeros(bars, dtype=int)  # 0 = range, 1 = up-trend, -1 = down-trend
    state = 0
    for i in range(1, bars):
        if rng.random() < 0.004:  # ~1 switch every 250 bars
            state = rng.choice([-1, 0, 1], p=[0.3, 0.4, 0.3])
        regime[i] = state

    vol = 0.6  # base per-bar volatility in price points
    close = np.empty(bars)
    close[0] = start_price
    for i in range(1, bars):
        # Volatility clusters (GARCH-like) and lifts during trends.
        target_vol = 0.6 + (0.9 if regime[i] != 0 else 0.0)
        vol = 0.94 * vol + 0.06 * target_vol + 0.02 * abs(rng.normal())
        drift = regime[i] * 0.10
        # Mean reversion toward a slow anchor when ranging keeps price bounded.
        anchor_pull = -0.02 * (close[i - 1] - start_price) if regime[i] == 0 else 0.0
        close[i] = close[i - 1] + drift + anchor_pull + rng.normal(0, vol)

    # Build OHLC around the close path.
    close = np.round(close, 2)
    open_ = np.empty(bars)
    open_[0] = start_price
    open_[1:] = close[:-1]
    # Independent upper/lower wicks so candles are asymmetric like real bars
    # (equal wicks would make rejection-candle detection impossible).
    body_hi = np.maximum(open_, close)
    body_lo = np.minimum(open_, close)
    upper_wick = np.abs(rng.normal(0, 0.6, bars)) + 0.05
    lower_wick = np.abs(rng.normal(0, 0.6, bars)) + 0.05
    high = body_hi + upper_wick
    low = body_lo - lower_wick
    # Volume rises with bar range — a rough stand-in for activity.
    bar_range = high - low
    volume = np.round(500 + 400 * bar_range + rng.normal(0, 50, bars).clip(0), 0)

    start = pd.Timestamp("2021-01-01 00:00")
    time = start + pd.to_timedelta(np.arange(bars) * timeframe_minutes, unit="m")

    return pd.DataFrame(
        {
            "time": time,
            "open": np.round(open_, 2),
            "high": np.round(high, 2),
            "low": np.round(low, 2),
            "close": close,
            "volume": volume,
        }
    )
