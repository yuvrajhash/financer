from __future__ import annotations

from dataclasses import dataclass

from financer.models import Regime, ScoreBreakdown, StrategySignal


@dataclass(slots=True)
class ContextScores:
    macro: float = 50.0
    global_fx: float = 50.0
    news_safety: float = 50.0
    liquidity: float = 70.0
    skeptic_penalty: float = 0.0


REGIME_FIT = {
    Regime.BREAKOUT: {"breakout_retest": 92, "trend_pullback": 68, "mean_reversion": 20},
    Regime.TREND_HIGH_VOL: {"breakout_retest": 85, "trend_pullback": 88, "mean_reversion": 20},
    Regime.TREND_LOW_VOL: {"breakout_retest": 60, "trend_pullback": 90, "mean_reversion": 30},
    Regime.RANGE_HIGH_VOL: {"breakout_retest": 55, "trend_pullback": 35, "mean_reversion": 72},
    Regime.RANGE_LOW_VOL: {"breakout_retest": 30, "trend_pullback": 25, "mean_reversion": 90},
    Regime.UNKNOWN: {},
}


class ScoringEngine:
    weights = {
        "technical": 0.30,
        "regime": 0.20,
        "macro": 0.12,
        "global_fx": 0.12,
        "news_safety": 0.14,
        "liquidity": 0.12,
    }

    def score(self, signal: StrategySignal, regime: Regime, context: ContextScores) -> ScoreBreakdown:
        regime_score = float(REGIME_FIT.get(regime, {}).get(signal.strategy, 40.0))
        components = {
            "technical": signal.technical_score,
            "regime": regime_score,
            "macro": context.macro,
            "global_fx": context.global_fx,
            "news_safety": context.news_safety,
            "liquidity": context.liquidity,
        }
        raw = sum(components[k] * self.weights[k] for k in self.weights)
        final = max(0.0, min(100.0, raw - context.skeptic_penalty))
        return ScoreBreakdown(
            technical=round(signal.technical_score, 2),
            regime=round(regime_score, 2),
            macro=round(context.macro, 2),
            global_fx=round(context.global_fx, 2),
            news_safety=round(context.news_safety, 2),
            liquidity=round(context.liquidity, 2),
            skeptic_penalty=round(context.skeptic_penalty, 2),
            final=round(final, 2),
        )
