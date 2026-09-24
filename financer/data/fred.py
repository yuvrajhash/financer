from __future__ import annotations

import httpx
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential


class FredClient:
    base_url = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("FRED_API_KEY is required")
        self.api_key = api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    def series(self, series_id: str, observation_start: str | None = None) -> pd.Series:
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "asc",
        }
        if observation_start:
            params["observation_start"] = observation_start
        with httpx.Client(timeout=15) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()
        rows = payload.get("observations", [])
        data = [(r["date"], None if r["value"] == "." else float(r["value"])) for r in rows]
        idx = pd.to_datetime([d for d, _ in data], utc=True)
        return pd.Series([v for _, v in data], index=idx, name=series_id, dtype="float64")
