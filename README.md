# FINANCER V0

Private AI-assisted FX research and **paper-trading** system for a 15-session validation experiment.

The first market is **USDINR futures**. Zerodha/Kite is used as the intended NSE execution/data source, while Twelve Data and FRED provide low-cost global FX and macro context. V0 does **not** place live orders.

## Design principles

- Deterministic code calculates prices, indicators, risk, P&L and strategy statistics.
- AI may critique or explain a setup, but it does not override hard risk rules.
- No look-ahead: a decision may only use information available at that timestamp.
- Every candidate setup, accepted or rejected, is journaled.
- Strategy changes must be versioned and backtested before they replace the active version.
- Paper execution includes configurable spread/slippage/cost assumptions.

## V0 strategies

1. Trend pullback
2. Breakout + retest / expansion
3. Mean reversion (range regimes only)

## Historical-data reality

Kite supports intraday history for live instruments, but expired futures do **not** have intraday continuous candles. FINANCER therefore separates:

- **actual NSE USDINR futures history** from the live contract;
- **forward data we archive ourselves** every day; and
- optional **USD/INR spot proxy history** for research only.

Proxy results are never treated as executable futures performance.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
python -m financer.cli init-db
python scripts/smoke_demo.py
pytest
```

## Historical backtest workflow

After adding your API credentials to `.env`:

```bash
# nearest live USDINR futures contract, actual Kite data
financer fetch-kite-usdinr --days 90

# causal backtest: signal at one bar close, entry at next bar open
financer backtest-csv data/usdinr_current_5m.csv

# optional spot proxy research
financer fetch-spot-usdinr
financer backtest-csv data/usdinr_spot_proxy_5m.csv --source-label spot-proxy-usdinr
```

The backtester includes configured slippage/cost assumptions and conservatively counts the stop first if stop and target are both inside the same OHLC bar.

## 15-session validation

V0 is a **go/no-go experiment**, not proof of a permanent edge. See `docs/VALIDATION_PLAN.md`.

## Credentials

Never commit secrets. Put them in `.env` only.

Required later:

- `KITE_API_KEY`
- `KITE_ACCESS_TOKEN`
- `TWELVE_DATA_API_KEY`
- `FRED_API_KEY`
- `OPENAI_API_KEY` (optional in V0)

## Current scope

V0 performs research and paper execution only. It contains no Zerodha order-placement code by design.
