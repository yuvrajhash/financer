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
