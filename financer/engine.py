from __future__ import annotations

import pandas as pd

from financer.agents.research import AIResearchReviewer
from financer.config import Settings
from financer.features.indicators import add_core_features
from financer.models import TradeCandidate
from financer.regimes.detector import RegimeDetector
from financer.risk.manager import RiskManager
from financer.scoring.engine import ContextScores, ScoringEngine
from financer.strategies import DEFAULT_STRATEGIES


class FinancerEngine:
    def __init__(self, settings: Settings, min_score: float = 72.0):
        self.s = settings
        self.min_score = min_score
        self.detector = RegimeDetector()
        self.scorer = ScoringEngine()
        self.risk = RiskManager(settings)
        self.ai = AIResearchReviewer(settings)
        self.strategies = DEFAULT_STRATEGIES

    def evaluate(
        self,
        bars: pd.DataFrame,
        context: ContextScores | None = None,
        equity: float | None = None,
        realized_pnl_today: float = 0.0,
        open_positions: int = 0,
        extra_context: dict | None = None,
    ) -> list[TradeCandidate]:
        context = context or ContextScores()
        equity = equity or self.s.paper_starting_capital
        f = add_core_features(bars)
        regime, _, _ = self.detector.detect(f)
        out: list[TradeCandidate] = []

        for strategy in self.strategies:
            signal = strategy.generate(f, regime)
            if not signal:
                continue
            score = self.scorer.score(signal, regime, context)
            risk = self.risk.evaluate(
                signal,
                equity=equity,
                realized_pnl_today=realized_pnl_today,
                open_positions=open_positions,
                min_score_passed=score.final >= self.min_score,
            )
            candidate = TradeCandidate(
                signal=signal,
                regime=regime,
                score=score,
                allowed=risk.allowed,
                rejection_reasons=risk.reasons,
            )
            candidate.ai_review = self.ai.review(candidate, extra_context)
            out.append(candidate)

        return sorted(out, key=lambda c: c.score.final, reverse=True)
