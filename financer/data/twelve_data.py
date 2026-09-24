from __future__ import annotations

import httpx
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential


class TwelveDataClient:
    base_url = "https://api.twelvedata.com"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("TWELVE_DATA_API_KEY is required")
        self.api_key = api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    def time_series(self, symbol: str, interval: str = "5min", outputsize: int = 300) -> pd.DataFrame:
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "timezone": "UTC",
            "apikey": self.api_key,
        }
        with httpx.Client(timeout=15) as client:
            response = client.get(f"{self.base_url}/time_series", params=params)
            response.raise_for_status()
            payload = response.json()
        if payload.get("status") == "error":
            raise RuntimeError(payload.get("message", "Twelve Data error"))
        values = payload.get("values") or []
        if not values:
            raise RuntimeError(f"No Twelve Data values returned for {symbol}")
        df = pd.DataFrame(values)
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        numeric = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
        df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce")
        return df.sort_values("datetime").set_index("datetime")
