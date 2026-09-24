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

## 15-session validation

V0 is a **go/no-go experiment**, not proof of a permanent edge. See `docs/VALIDATION_PLAN.md`.

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
