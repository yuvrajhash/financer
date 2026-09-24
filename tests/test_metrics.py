import pandas as pd

from financer.evaluation.metrics import calculate_metrics


def test_metrics_computes_expectancy_and_drawdown():
    df = pd.DataFrame(
        {
            "status": ["CLOSED"] * 5,
            "r_multiple": [2.0, -1.0, 1.5, -1.0, 2.0],
            "pnl": [1000, -500, 750, -500, 1000],
        }
    )
    m = calculate_metrics(df)
    assert m.trades == 5
    assert m.wins == 3
    assert m.expectancy_r == 0.7
    assert m.max_drawdown_r == 1.0
    assert m.profit_factor == 2.75
