from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from financer.models import Regime, StrategySignal


class Strategy(ABC):
    name: str
    version: str

    @abstractmethod
    def generate(self, df: pd.DataFrame, regime: Regime) -> StrategySignal | None:
        raise NotImplementedError
