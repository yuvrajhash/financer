from __future__ import annotations

from financer.backtest.runner import BacktestResult


def render_backtest_report(result: BacktestResult) -> str:
    m = result.metrics
    pf = "inf" if m.profit_factor == float("inf") else f"{m.profit_factor:.2f}"
    lines = [
        "FINANCER BACKTEST",
        f"Source: {result.source_label}",
        f"Closed trades: {m.trades}",
        f"Win rate: {m.win_rate_pct:.2f}%",
        f"Net R: {m.net_r:.2f}",
        f"Expectancy: {m.expectancy_r:.3f}R/trade",
        f"Profit factor: {pf}",
        f"Max drawdown: {m.max_drawdown_r:.2f}R",
        f"Average winner: {m.average_win_r:.2f}R",
        f"Average loser: {m.average_loss_r:.2f}R",
        f"Candidates observed: {len(result.candidates)}",
    ]
    if result.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {w}" for w in result.warnings)
    return "\n".join(lines)
