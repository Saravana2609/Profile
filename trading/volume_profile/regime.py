"""Trend-vs-range regime detection.

Reversion trades at Value-Area edges only work when the market is ranging; in
a trend they get run over. This module labels each bar's regime so the strategy
can stand aside (or flip to breakout logic) when price is trending.

Two detectors are provided:

- ``adx_regime``: a transparent rule-based filter (ADX + slope). No training,
  good default, easy to reason about.
- ``RegimeModel``: an optional ML classifier (logistic regression) trained on
  simple features, for when you want a data-driven filter. Kept dependency-light
  so it runs anywhere.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def atr(bars: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = bars["high"], bars["low"], bars["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def adx(bars: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average Directional Index — measures trend strength (not direction)."""
    high, low, close = bars["high"], bars["low"], bars["close"]
    up = high.diff()
    down = -low.diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)

    tr = pd.concat(
        [high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1
    ).max(axis=1)
    atr_ = tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    plus_di = 100 * pd.Series(plus_dm, index=bars.index).ewm(
        alpha=1 / period, adjust=False, min_periods=period
    ).mean() / atr_
    minus_di = 100 * pd.Series(minus_dm, index=bars.index).ewm(
        alpha=1 / period, adjust=False, min_periods=period
    ).mean() / atr_

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def adx_regime(bars: pd.DataFrame, adx_threshold: float = 25.0, period: int = 14) -> pd.Series:
    """Boolean series: True where the market is RANGING (safe to fade levels).

    ADX below the threshold => weak trend => ranging. This is the default
    regime filter and needs no training.
    """
    return adx(bars, period) < adx_threshold


def regime_features(bars: pd.DataFrame) -> pd.DataFrame:
    """Features describing trendiness, for the optional ML regime model."""
    close = bars["close"]
    feat = pd.DataFrame(index=bars.index)
    feat["adx"] = adx(bars)
    feat["atr_pct"] = atr(bars) / close
    # Efficiency ratio: net move / summed path. ~1 = clean trend, ~0 = chop.
    window = 20
    net = close.diff(window).abs()
    path = close.diff().abs().rolling(window).sum()
    feat["efficiency"] = (net / path.replace(0, np.nan)).clip(0, 1)
    # Distance of price from its own moving average, in ATR units.
    ma = close.rolling(20).mean()
    feat["ma_dist_atr"] = (close - ma) / atr(bars)
    feat["ret_std"] = close.pct_change().rolling(20).std()
    return feat


class RegimeModel:
    """Optional logistic-regression trend/range classifier.

    Labels are self-supervised from *future* efficiency ratio at train time
    only (never at inference), so there is no lookahead in live use.
    """

    def __init__(self):
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline

        self.model = make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000)
        )
        self.fitted = False

    @staticmethod
    def _label_ranging(bars: pd.DataFrame, horizon: int = 20) -> pd.Series:
        """1 if the next `horizon` bars are choppy (low efficiency), else 0."""
        close = bars["close"]
        fwd_net = close.shift(-horizon).sub(close).abs()
        fwd_path = close.diff().abs().shift(-1).rolling(horizon).sum().shift(-(horizon - 1))
        eff = fwd_net / fwd_path.replace(0, np.nan)
        return (eff < 0.35).astype(int)

    def fit(self, bars: pd.DataFrame) -> "RegimeModel":
        X = regime_features(bars)
        y = self._label_ranging(bars)
        data = X.join(y.rename("y")).dropna()
        self.model.fit(data.drop(columns="y"), data["y"])
        self.fitted = True
        return self

    def predict_ranging(self, bars: pd.DataFrame) -> pd.Series:
        if not self.fitted:
            raise RuntimeError("Call fit() before predict_ranging()")
        X = regime_features(bars)
        valid = X.dropna()
        proba = pd.Series(np.nan, index=bars.index)
        if len(valid):
            proba.loc[valid.index] = self.model.predict_proba(valid)[:, 1]
        return proba
