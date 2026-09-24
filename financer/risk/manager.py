from __future__ import annotations

from dataclasses import dataclass

from financer.config import Settings
from financer.models import StrategySignal


@dataclass(slots=True)
class RiskDecision:
    allowed: bool
    quantity: int
    risk_budget: float
    reasons: list[str]


class RiskManager:
    def __init__(self, settings: Settings):
        self.s = settings

    def evaluate(
        self,
        signal: StrategySignal,
        equity: float,
        realized_pnl_today: float,
        open_positions: int,
        min_score_passed: bool,
    ) -> RiskDecision:
        reasons: list[str] = []
        if open_positions >= self.s.max_open_positions:
            reasons.append("maximum open positions reached")
        daily_limit = equity * self.s.max_daily_loss_pct / 100
        if realized_pnl_today <= -daily_limit:
            reasons.append("daily loss limit reached")
        if not min_score_passed:
            reasons.append("setup score below threshold")
        if signal.risk_distance <= 0:
            reasons.append("invalid stop distance")
        if signal.rr < 1.35:
            reasons.append(f"R:R too low ({signal.rr:.2f})")

        risk_budget = equity * self.s.max_risk_per_trade_pct / 100
        raw_units = 0 if signal.risk_distance <= 0 else int(risk_budget / signal.risk_distance)
        lots = raw_units // self.s.paper_lot_size
        quantity = max(0, lots * self.s.paper_lot_size)
        if quantity <= 0:
            reasons.append("risk budget cannot support one configured lot")

        return RiskDecision(not reasons, quantity, round(risk_budget, 2), reasons)
