"""Volume Profile backtesting toolkit for XAUUSD (and any OHLCV symbol)."""

from .data import generate_synthetic, load_from_csv, load_from_mt5, resample_ohlcv
from .profile import VolumeProfile, build_profile
from .regime import RegimeModel, adx, adx_regime, atr
from .strategy import Signal, StrategyConfig, generate_signals
from .backtest import CostModel, Trade, run_backtest

__all__ = [
    "generate_synthetic",
    "load_from_csv",
    "load_from_mt5",
    "resample_ohlcv",
    "VolumeProfile",
    "build_profile",
    "RegimeModel",
    "adx",
    "adx_regime",
    "atr",
    "Signal",
    "StrategyConfig",
    "generate_signals",
    "CostModel",
    "Trade",
    "run_backtest",
]
