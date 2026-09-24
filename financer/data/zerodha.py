from __future__ import annotations

from datetime import datetime

import pandas as pd
from kiteconnect import KiteConnect


class ZerodhaDataClient:
    """Read-only Kite adapter for V0.

    V0 intentionally exposes no order-placement method.
    """

    def __init__(self, api_key: str, access_token: str):
        if not api_key or not access_token:
            raise ValueError("KITE_API_KEY and KITE_ACCESS_TOKEN are required")
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

    def historical(
        self,
        instrument_token: int,
        from_date: datetime,
        to_date: datetime,
        interval: str = "5minute",
        oi: bool = True,
    ) -> pd.DataFrame:
        rows = self.kite.historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
            continuous=False,
            oi=oi,
        )
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df["date"] = pd.to_datetime(df["date"], utc=True)
        df = df.rename(columns={"date": "datetime", "oi": "open_interest"})
        return df.set_index("datetime").sort_index()

    def instruments(self, exchange: str = "CDS") -> pd.DataFrame:
        return pd.DataFrame(self.kite.instruments(exchange))
