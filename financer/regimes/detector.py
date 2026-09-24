from __future__ import annotations

import pandas as pd

from financer.features.indicators import add_core_features
from financer.models import Regime


class RegimeDetector:
    def detect(self, df: pd.DataFrame) -> tuple[Regime, float, dict[str, float]]:
        f = add_core_features(df) if "adx14" not in df.columns else df
        if len(f) < 55:
            return Regime.UNKNOWN, 0.0, {}

        row = f.iloc[-1]
        if pd.isna(row["atr14"]) or pd.isna(row["ema50"]):
            return Regime.UNKNOWN, 0.0, {}

        adx = float(row["adx14"])
        atr_pct = float(row["atr_pct"]) if not pd.isna(row["atr_pct"]) else 50.0
        ema_gap_atr = abs(float(row["ema20"] - row["ema50"])) / max(float(row["atr14"]), 1e-9)

        prior_high = float(row["range20_high"]) if not pd.isna(row["range20_high"]) else float("inf")
        prior_low = float(row["range20_low"]) if not pd.isna(row["range20_low"]) else float("-inf")
        close = float(row["close"])
        breakout = close > prior_high or close < prior_low

        if breakout and atr_pct >= 60:
            regime = Regime.BREAKOUT
            confidence = min(100.0, 65 + (atr_pct - 60) * 0.5 + min(adx, 35) * 0.4)
        elif adx >= 23 and ema_gap_atr >= 0.35:
            regime = Regime.TREND_HIGH_VOL if atr_pct >= 60 else Regime.TREND_LOW_VOL
            confidence = min(100.0, 50 + adx + min(ema_gap_atr * 10, 15))
        else:
            regime = Regime.RANGE_HIGH_VOL if atr_pct >= 60 else Regime.RANGE_LOW_VOL
            confidence = min(100.0, 75 - min(adx, 30) + abs(50 - atr_pct) * 0.15)

        meta = {"adx": adx, "atr_percentile": atr_pct, "ema_gap_atr": ema_gap_atr}
        return regime, round(confidence, 2), meta
