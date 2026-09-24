from datetime import datetime, timezone

from financer.config import Settings
from financer.models import Side, StrategySignal
from financer.paper.broker import PaperBroker


def test_stop_wins_when_stop_and_target_same_bar():
    s = Settings(paper_tick_size=0, paper_slippage_ticks=0, paper_round_trip_cost=0)
    broker = PaperBroker(s)
    signal = StrategySignal("x", "1", Side.LONG, datetime.now(timezone.utc), 100, 99, 102, 80)
    trade = broker.open(signal, quantity=1000, score=80)
    broker.mark_bar(datetime.now(timezone.utc), high=103, low=98)
    assert trade.exit_reason == "STOP"
    assert trade.pnl < 0
