from __future__ import annotations

import pandas as pd

from financer.features.indicators import add_core_features
from financer.models import Regime, Side, StrategySignal
from financer.strategies.base import Strategy


class TrendPullbackStrategy(Strategy):
    name = "trend_pullback"
    version = "1.0.0"

    def generate(self, df: pd.DataFrame, regime: Regime) -> StrategySignal | None:
        if regime not in {Regime.TREND_LOW_VOL, Regime.TREND_HIGH_VOL}:
            return None
        f = add_core_features(df) if "ema20" not in df.columns else df
        if len(f) < 55:
            return None
        r = f.iloc[-1]
        if any(pd.isna(r[k]) for k in ["ema20", "ema50", "atr14", "rsi14"]):
            return None

        close, e20, e50, atr, rsi = map(float, [r.close, r.ema20, r.ema50, r.atr14, r.rsi14])
        near_ema = abs(close - e20) <= 0.55 * atr
        ts = r.name.to_pydatetime() if hasattr(r.name, "to_pydatetime") else pd.Timestamp.utcnow().to_pydatetime()

        if e20 > e50 and near_ema and 43 <= rsi <= 64 and close >= e20 * 0.999:
            stop = close - 1.15 * atr
            target = close + 2.0 * (close - stop)
            return StrategySignal(self.name, self.version, Side.LONG, ts, close, stop, target, 74.0,
                                  ["EMA20 above EMA50", "pullback near EMA20", "RSI not overbought"])
        if e20 < e50 and near_ema and 36 <= rsi <= 57 and close <= e20 * 1.001:
            stop = close + 1.15 * atr
            target = close - 2.0 * (stop - close)
            return StrategySignal(self.name, self.version, Side.SHORT, ts, close, stop, target, 74.0,
                                  ["EMA20 below EMA50", "pullback near EMA20", "RSI not oversold"])
        return None
