from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(slots=True)
class PerformanceMetrics:
    trades: int
    wins: int
    losses: int
    win_rate_pct: float
    net_pnl: float
    net_r: float
    expectancy_r: float
    average_win_r: float
    average_loss_r: float
    profit_factor: float
    max_drawdown_r: float

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_metrics(trades: pd.DataFrame) -> PerformanceMetrics:
    if trades.empty:
        return PerformanceMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    closed = trades[trades["status"] == "CLOSED"].copy() if "status" in trades.columns else trades.copy()
    if closed.empty:
        return PerformanceMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    r = pd.to_numeric(closed["r_multiple"], errors="coerce").fillna(0.0)
    pnl = pd.to_numeric(closed["pnl"], errors="coerce").fillna(0.0)
    wins = r[r > 0]
    losses = r[r < 0]
    equity_r = r.cumsum()
    running_max = equity_r.cummax().clip(lower=0)
    drawdown = equity_r - running_max

    gross_profit = float(pnl[pnl > 0].sum())
    gross_loss = abs(float(pnl[pnl < 0].sum()))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else (float("inf") if gross_profit > 0 else 0.0)

    return PerformanceMetrics(
        trades=int(len(closed)),
        wins=int((r > 0).sum()),
        losses=int((r < 0).sum()),
        win_rate_pct=round(float((r > 0).mean() * 100), 2),
        net_pnl=round(float(pnl.sum()), 2),
        net_r=round(float(r.sum()), 4),
        expectancy_r=round(float(r.mean()), 4),
        average_win_r=round(float(wins.mean()), 4) if not wins.empty else 0.0,
        average_loss_r=round(float(losses.mean()), 4) if not losses.empty else 0.0,
        profit_factor=round(profit_factor, 4) if np.isfinite(profit_factor) else float("inf"),
        max_drawdown_r=round(abs(float(drawdown.min())), 4),
    )
