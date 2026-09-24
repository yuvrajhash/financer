from datetime import date

import pandas as pd

from financer.data.contracts import select_nearest_future


def test_select_nearest_future():
    df = pd.DataFrame(
        [
            {
                "instrument_token": 1, "tradingsymbol": "USDINR26OCTFUT", "name": "USDINR",
                "expiry": "2026-10-28", "lot_size": 1000, "tick_size": 0.0025,
                "instrument_type": "FUT", "exchange": "CDS", "segment": "CDS-FUT",
            },
            {
                "instrument_token": 2, "tradingsymbol": "USDINR26NOVFUT", "name": "USDINR",
                "expiry": "2026-11-27", "lot_size": 1000, "tick_size": 0.0025,
                "instrument_type": "FUT", "exchange": "CDS", "segment": "CDS-FUT",
            },
        ]
    )
    c = select_nearest_future(df, as_of=date(2026, 9, 24))
    assert c.instrument_token == 1
    assert c.tradingsymbol == "USDINR26OCTFUT"
