from __future__ import annotations

import pandas as pd

from financer.features.indicators import add_core_features
from financer.models import Regime, Side, StrategySignal
from financer.strategies.base import Strategy


class MeanReversionStrategy(Strategy):
    name = "mean_reversion"
    version = "1.0.0"

    def generate(self, df: pd.DataFrame, regime: Regime) -> StrategySignal | None:
        if regime not in {Regime.RANGE_LOW_VOL, Regime.RANGE_HIGH_VOL}:
            return None
        f = add_core_features(df) if "sma20" not in df.columns else df
        if len(f) < 25:
            return None
        r = f.iloc[-1]
        if any(pd.isna(r[k]) for k in ["sma20", "std20", "atr14", "rsi14", "adx14"]):
            return None

        close, mean, std, atr, rsi, adx = map(float, [r.close, r.sma20, r.std20, r.atr14, r.rsi14, r.adx14])
        if std <= 0 or adx > 22:
            return None
        z = (close - mean) / std
        ts = r.name.to_pydatetime() if hasattr(r.name, "to_pydatetime") else pd.Timestamp.utcnow().to_pydatetime()

        if z <= -1.8 and rsi <= 36:
            stop = close - 0.95 * atr
            target = mean
            if target <= close:
                return None
            return StrategySignal(self.name, self.version, Side.LONG, ts, close, stop, target, 70.0,
                                  ["range regime", f"z-score {z:.2f}", "RSI oversold"])
        if z >= 1.8 and rsi >= 64:
            stop = close + 0.95 * atr
            target = mean
            if target >= close:
                return None
            return StrategySignal(self.name, self.version, Side.SHORT, ts, close, stop, target, 70.0,
                                  ["range regime", f"z-score {z:.2f}", "RSI overbought"])
        return None
