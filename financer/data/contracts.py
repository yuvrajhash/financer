from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True, slots=True)
class FuturesContract:
    instrument_token: int
    tradingsymbol: str
    name: str
    expiry: date
    lot_size: int
    tick_size: float
    exchange: str
    segment: str


def select_nearest_future(
    instruments: pd.DataFrame,
    underlying: str = "USDINR",
    as_of: date | None = None,
) -> FuturesContract:
    """Select the nearest non-expired futures contract from a Kite instrument dump."""
    as_of = as_of or date.today()
    if instruments.empty:
        raise ValueError("Empty instrument dump")

    df = instruments.copy()
    required = {
        "instrument_token", "tradingsymbol", "name", "expiry", "lot_size",
        "tick_size", "instrument_type", "exchange", "segment",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Instrument dump missing fields: {sorted(missing)}")

    df["expiry"] = pd.to_datetime(df["expiry"], errors="coerce").dt.date
    name_match = df["name"].astype(str).str.upper().eq(underlying.upper())
    symbol_match = df["tradingsymbol"].astype(str).str.upper().str.startswith(underlying.upper())
    fut = df[
        (df["instrument_type"].astype(str).str.upper() == "FUT")
        & (name_match | symbol_match)
        & df["expiry"].notna()
        & (df["expiry"] >= as_of)
    ].sort_values("expiry")

    if fut.empty:
        raise LookupError(f"No live {underlying} futures contract found")

    r = fut.iloc[0]
    return FuturesContract(
        instrument_token=int(r["instrument_token"]),
        tradingsymbol=str(r["tradingsymbol"]),
        name=str(r["name"]),
        expiry=r["expiry"],
        lot_size=int(r["lot_size"]),
        tick_size=float(r["tick_size"]),
        exchange=str(r["exchange"]),
        segment=str(r["segment"]),
    )
