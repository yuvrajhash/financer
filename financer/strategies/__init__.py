from financer.strategies.breakout_retest import BreakoutRetestStrategy
from financer.strategies.mean_reversion import MeanReversionStrategy
from financer.strategies.trend_pullback import TrendPullbackStrategy

DEFAULT_STRATEGIES = [TrendPullbackStrategy(), BreakoutRetestStrategy(), MeanReversionStrategy()]

__all__ = ["DEFAULT_STRATEGIES", "TrendPullbackStrategy", "BreakoutRetestStrategy", "MeanReversionStrategy"]
