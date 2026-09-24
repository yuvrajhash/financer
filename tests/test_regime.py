import numpy as np
import pandas as pd

from financer.regimes.detector import RegimeDetector
from financer.models import Regime


def test_regime_detector_returns_known_value():
    rng = np.random.default_rng(1)
    idx = pd.date_range("2026-01-01", periods=160, freq="5min", tz="UTC")
    close = 88 + np.linspace(0, 1.2, len(idx)) + rng.normal(0, 0.01, len(idx))
    open_ = np.r_[close[0], close[:-1]]
    df = pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) + 0.01,
            "low": np.minimum(open_, close) - 0.01,
            "close": close,
            "volume": 1000,
        },
        index=idx,
    )
    regime, confidence, _ = RegimeDetector().detect(df)
    assert regime != Regime.UNKNOWN
    assert confidence > 0
