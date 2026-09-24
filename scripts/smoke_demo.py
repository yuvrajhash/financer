from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from financer.config import Settings
from financer.engine import FinancerEngine
from financer.scoring.engine import ContextScores


rng = np.random.default_rng(7)
idx = pd.date_range("2026-09-01 09:00", periods=220, freq="5min", tz="Asia/Kolkata")
base = 88.0 + np.linspace(0, 0.65, len(idx)) + rng.normal(0, 0.015, len(idx)).cumsum()
open_ = np.r_[base[0], base[:-1]]
close = base
high = np.maximum(open_, close) + rng.uniform(0.004, 0.018, len(idx))
low = np.minimum(open_, close) - rng.uniform(0.004, 0.018, len(idx))
volume = rng.integers(500, 3000, len(idx))

df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume}, index=idx)
engine = FinancerEngine(Settings(enable_ai_review=False), min_score=65)
candidates = engine.evaluate(
    df,
    ContextScores(macro=62, global_fx=66, news_safety=80, liquidity=82),
)
print(f"Generated {len(candidates)} candidate(s)")
for c in candidates:
    print(c.signal.strategy, c.signal.side, c.score.final, c.regime, c.allowed, c.rejection_reasons)
