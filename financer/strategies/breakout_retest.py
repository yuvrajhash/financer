from __future__ import annotations

import pandas as pd

from financer.features.indicators import add_core_features
from financer.models import Regime, Side, StrategySignal
from financer.strategies.base import Strategy


class BreakoutRetestStrategy(Strategy):
    name = "breakout_retest"
    version = "1.0.0"

    def generate(self, df: pd.DataFrame, regime: Regime) -> StrategySignal | None:
        if regime not in {Regime.BREAKOUT, Regime.TREND_HIGH_VOL}:
            return None
        f = add_core_features(df) if "range20_high" not in df.columns else df
        if len(f) < 25:
            return None
        r = f.iloc[-1]
        needed = ["atr14", "range20_high", "range20_low"]
        if any(pd.isna(r[k]) for k in needed):
            return None

        close = float(r.close)
        atr = float(r.atr14)
        hi = float(r.range20_high)
        lo = float(r.range20_low)
        volume_ok = True
        if float(r.volume20 or 0) > 0:
            volume_ok = float(r.volume) >= 1.05 * float(r.volume20)
        ts = r.name.to_pydatetime() if hasattr(r.name, "to_pydatetime") else pd.Timestamp.utcnow().to_pydatetime()

        if close > hi + 0.10 * atr and volume_ok:
            stop = close - 1.0 * atr
            target = close + 2.1 * atr
            return StrategySignal(self.name, self.version, Side.LONG, ts, close, stop, target, 78.0,
                                  ["20-bar upside breakout", "volatility expansion", "volume confirmation"])
        if close < lo - 0.10 * atr and volume_ok:
            stop = close + 1.0 * atr
            target = close - 2.1 * atr
            return StrategySignal(self.name, self.version, Side.SHORT, ts, close, stop, target, 78.0,
                                  ["20-bar downside breakout", "volatility expansion", "volume confirmation"])
        return None
