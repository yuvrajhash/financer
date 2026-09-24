from datetime import datetime, timezone

from financer.config import Settings
from financer.models import Side, StrategySignal
from financer.risk.manager import RiskManager


def test_daily_loss_blocks_trade():
    s = Settings(paper_starting_capital=100000, max_daily_loss_pct=1.5, paper_lot_size=1000)
    signal = StrategySignal("x", "1", Side.LONG, datetime.now(timezone.utc), 88, 87.95, 88.12, 80)
    d = RiskManager(s).evaluate(signal, 100000, -1600, 0, True)
    assert not d.allowed
    assert any("daily loss" in reason for reason in d.reasons)
