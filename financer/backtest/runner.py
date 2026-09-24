from __future__ import annotations

from dataclasses import dataclass, field, replace

import pandas as pd

from financer.config import Settings
from financer.engine import FinancerEngine
from financer.evaluation.metrics import PerformanceMetrics, calculate_metrics
from financer.models import PaperTrade, StrategySignal, TradeCandidate
from financer.paper.broker import PaperBroker
from financer.risk.manager import RiskManager
from financer.scoring.engine import ContextScores


@dataclass(slots=True)
class BacktestResult:
    trades: list[PaperTrade]
    candidates: list[TradeCandidate]
    metrics: PerformanceMetrics
    source_label: str
    warnings: list[str] = field(default_factory=list)


class BacktestRunner:
    """Causal bar-by-bar backtest.

    A setup is calculated only after bar i closes. If accepted, entry occurs at bar i+1
    open with configured slippage. Stops/targets preserve the strategy's planned risk
    distances from the new fill reference. This prevents same-close fills and look-ahead.
    """

    def __init__(
        self,
        settings: Settings,
        min_score: float = 72.0,
        warmup_bars: int = 120,
    ):
        self.s = settings
        self.engine = FinancerEngine(settings, min_score=min_score)
        self.risk = RiskManager(settings)
        self.warmup_bars = warmup_bars

    @staticmethod
    def _reprice_signal(signal: StrategySignal, next_open: float) -> StrategySignal:
        risk = signal.risk_distance
        reward = signal.reward_distance
        if signal.side.value == "LONG":
            stop = next_open - risk
            target = next_open + reward
        else:
            stop = next_open + risk
            target = next_open - reward
        return replace(signal, entry=float(next_open), stop=float(stop), target=float(target))

    def run(
        self,
        bars: pd.DataFrame,
        context: ContextScores | None = None,
        source_label: str = "unknown",
    ) -> BacktestResult:
        if len(bars) <= self.warmup_bars + 2:
            raise ValueError("Not enough bars for backtest")

        df = bars.sort_index().copy()
        required = {"open", "high", "low", "close"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")

        context = context or ContextScores()
        broker = PaperBroker(self.s)
        candidates_seen: list[TradeCandidate] = []
        equity = self.s.paper_starting_capital
        realized_today = 0.0
        current_day = None

        for i in range(self.warmup_bars, len(df) - 1):
            now = df.index[i]
            next_ts = df.index[i + 1]
            next_bar = df.iloc[i + 1]

            day = pd.Timestamp(now).date()
            if current_day != day:
                current_day = day
                realized_today = 0.0

            # If a position was already open before next_bar started, the strategy cannot
            # also claim a new fill at next_bar's open even if that old trade exits later
            # inside the same candle.
            had_open_before_next_bar = bool(broker.open_trades)
            if had_open_before_next_bar:
                just_closed = broker.mark_bar(
                    pd.Timestamp(next_ts).to_pydatetime(),
                    float(next_bar["high"]),
                    float(next_bar["low"]),
                )
                for t in just_closed:
                    equity += t.pnl
                    realized_today += t.pnl
                continue

            window = df.iloc[: i + 1]
            found = self.engine.evaluate(
                window,
                context=context,
                equity=equity,
                realized_pnl_today=realized_today,
                open_positions=0,
            )
            candidates_seen.extend(found)
            accepted = next((c for c in found if c.allowed), None)
            if not accepted:
                continue

            repriced = self._reprice_signal(accepted.signal, float(next_bar["open"]))
            risk = self.risk.evaluate(
                repriced,
                equity=equity,
                realized_pnl_today=realized_today,
                open_positions=0,
                min_score_passed=accepted.score.final >= self.engine.min_score,
            )
            if not risk.allowed:
                continue

            broker.open(repriced, risk.quantity, accepted.score.final)

            # Entry occurs at next_bar open. The bar's high/low are then eligible to hit
            # stop/target. If both occur, PaperBroker deliberately assumes stop first.
            immediate = broker.mark_bar(
                pd.Timestamp(next_ts).to_pydatetime(),
                float(next_bar["high"]),
                float(next_bar["low"]),
            )
            for t in immediate:
                equity += t.pnl
                realized_today += t.pnl

        if broker.open_trades:
            last_ts = pd.Timestamp(df.index[-1]).to_pydatetime()
            last_close = float(df.iloc[-1]["close"])
            for trade_id in list(broker.open_trades):
                t = broker.close_market(trade_id, last_ts, last_close, "END_OF_DATA")
                equity += t.pnl

        trades_df = pd.DataFrame(
            [
                {
                    "status": t.status,
                    "pnl": t.pnl,
                    "r_multiple": t.r_multiple,
                }
                for t in broker.closed_trades
            ]
        )
        metrics = calculate_metrics(trades_df)
        warnings: list[str] = []
        if "proxy" in source_label.lower():
            warnings.append(
                "Proxy-market results are research-only and must not be treated as executable "
                "NSE USDINR futures performance."
            )
        return BacktestResult(broker.closed_trades, candidates_seen, metrics, source_label, warnings)
