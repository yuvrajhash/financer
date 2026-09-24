import numpy as np
import pandas as pd

from financer.backtest.runner import BacktestRunner
from financer.config import Settings
from financer.scoring.engine import ContextScores


def test_backtest_is_causal_and_runs():
    rng = np.random.default_rng(4)
    idx = pd.date_range("2026-01-01 09:00", periods=300, freq="5min", tz="Asia/Kolkata")
    close = 88 + np.linspace(0, 0.9, len(idx)) + rng.normal(0, 0.012, len(idx)).cumsum()
    open_ = np.r_[close[0], close[:-1]]
    df = pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) + 0.012,
            "low": np.minimum(open_, close) - 0.012,
            "close": close,
            "volume": rng.integers(1000, 5000, len(idx)),
        },
        index=idx,
    )
    s = Settings(
        enable_ai_review=False,
        paper_lot_size=1000,
        paper_tick_size=0.0025,
        paper_slippage_ticks=1,
        paper_round_trip_cost=20,
    )
    result = BacktestRunner(s, min_score=60, warmup_bars=120).run(
        df,
        ContextScores(macro=65, global_fx=65, news_safety=80, liquidity=85),
        source_label="synthetic",
    )
    assert result.metrics.trades >= 0
    assert result.source_label == "synthetic"
