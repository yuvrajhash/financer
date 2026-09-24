from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from financer.config import Settings
from financer.models import PaperTrade, Side, StrategySignal


class PaperBroker:
    """Conservative bar-based paper executor.

    If both stop and target are touched inside one OHLC bar and intrabar order is unknown,
    the stop is assumed to have been hit first. This intentionally avoids optimistic bias.
    """

    def __init__(self, settings: Settings):
        self.s = settings
        self.open_trades: dict[str, PaperTrade] = {}
        self.closed_trades: list[PaperTrade] = []

    def _slippage(self) -> float:
        return self.s.paper_tick_size * self.s.paper_slippage_ticks

    def open(self, signal: StrategySignal, quantity: int, score: float) -> PaperTrade:
        slip = self._slippage()
        fill = signal.entry + slip if signal.side == Side.LONG else signal.entry - slip
        trade = PaperTrade(
            id=str(uuid4()),
            strategy=signal.strategy,
            strategy_version=signal.strategy_version,
            side=signal.side,
            opened_at=signal.generated_at,
            entry=fill,
            stop=signal.stop,
            target=signal.target,
            quantity=quantity,
            score=score,
        )
        self.open_trades[trade.id] = trade
        return trade

    def mark_bar(self, timestamp: datetime, high: float, low: float) -> list[PaperTrade]:
        closed: list[PaperTrade] = []
        for trade in list(self.open_trades.values()):
            stop_hit = low <= trade.stop if trade.side == Side.LONG else high >= trade.stop
            target_hit = high >= trade.target if trade.side == Side.LONG else low <= trade.target

            if stop_hit:
                self._close(trade, timestamp, trade.stop, "STOP")
                closed.append(trade)
            elif target_hit:
                self._close(trade, timestamp, trade.target, "TARGET")
                closed.append(trade)
        return closed

    def close_market(self, trade_id: str, timestamp: datetime, price: float, reason: str = "MANUAL") -> PaperTrade:
        trade = self.open_trades[trade_id]
        self._close(trade, timestamp, price, reason)
        return trade

    def _close(self, trade: PaperTrade, timestamp: datetime, raw_exit: float, reason: str) -> None:
        slip = self._slippage()
        exit_price = raw_exit - slip if trade.side == Side.LONG else raw_exit + slip
        direction = 1 if trade.side == Side.LONG else -1
        gross = direction * (exit_price - trade.entry) * trade.quantity
        net = gross - self.s.paper_round_trip_cost
        risk_cash = abs(trade.entry - trade.stop) * trade.quantity

        trade.exit_price = exit_price
        trade.closed_at = timestamp
        trade.pnl = round(net, 2)
        trade.r_multiple = round(net / risk_cash, 4) if risk_cash > 0 else 0.0
        trade.exit_reason = reason
        trade.status = "CLOSED"
        self.open_trades.pop(trade.id, None)
        self.closed_trades.append(trade)
