from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class Side(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


class Regime(StrEnum):
    TREND_LOW_VOL = "TREND_LOW_VOL"
    TREND_HIGH_VOL = "TREND_HIGH_VOL"
    RANGE_LOW_VOL = "RANGE_LOW_VOL"
    RANGE_HIGH_VOL = "RANGE_HIGH_VOL"
    BREAKOUT = "BREAKOUT"
    UNKNOWN = "UNKNOWN"


@dataclass(slots=True)
class StrategySignal:
    strategy: str
    strategy_version: str
    side: Side
    generated_at: datetime
    entry: float
    stop: float
    target: float
    technical_score: float
    reasons: list[str] = field(default_factory=list)

    @property
    def risk_distance(self) -> float:
        return abs(self.entry - self.stop)

    @property
    def reward_distance(self) -> float:
        return abs(self.target - self.entry)

    @property
    def rr(self) -> float:
        if self.risk_distance <= 0:
            return 0.0
        return self.reward_distance / self.risk_distance


@dataclass(slots=True)
class ScoreBreakdown:
    technical: float
    regime: float
    macro: float
    global_fx: float
    news_safety: float
    liquidity: float
    skeptic_penalty: float
    final: float


@dataclass(slots=True)
class TradeCandidate:
    signal: StrategySignal
    regime: Regime
    score: ScoreBreakdown
    allowed: bool
    rejection_reasons: list[str] = field(default_factory=list)
    ai_review: str | None = None


@dataclass(slots=True)
class PaperTrade:
    id: str
    strategy: str
    strategy_version: str
    side: Side
    opened_at: datetime
    entry: float
    stop: float
    target: float
    quantity: int
    score: float
    status: str = "OPEN"
    closed_at: datetime | None = None
    exit_price: float | None = None
    pnl: float = 0.0
    r_multiple: float = 0.0
    exit_reason: str | None = None
