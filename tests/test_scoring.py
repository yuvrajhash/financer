from datetime import datetime, timezone

import pytest

from financer.models import Regime, Side, StrategySignal
from financer.scoring.engine import ContextScores, ScoringEngine


def test_score_penalty_lowers_final():
    signal = StrategySignal("trend_pullback", "1", Side.LONG, datetime.now(timezone.utc), 88, 87.9, 88.2, 80)
    engine = ScoringEngine()
    a = engine.score(signal, Regime.TREND_LOW_VOL, ContextScores(skeptic_penalty=0))
    b = engine.score(signal, Regime.TREND_LOW_VOL, ContextScores(skeptic_penalty=12))
    assert b.final == pytest.approx(a.final - 12)


def test_usd_bullish_context_helps_long_and_hurts_short():
    engine = ScoringEngine()
    context = ContextScores(macro=80, global_fx=75, news_safety=80, liquidity=80)
    long_signal = StrategySignal("trend_pullback", "1", Side.LONG, datetime.now(timezone.utc), 88, 87.9, 88.2, 80)
    short_signal = StrategySignal("trend_pullback", "1", Side.SHORT, datetime.now(timezone.utc), 88, 88.1, 87.8, 80)

    long_score = engine.score(long_signal, Regime.TREND_LOW_VOL, context)
    short_score = engine.score(short_signal, Regime.TREND_LOW_VOL, context)

    assert long_score.macro == 80
    assert short_score.macro == 20
    assert long_score.global_fx == 75
    assert short_score.global_fx == 25
    assert long_score.final > short_score.final
