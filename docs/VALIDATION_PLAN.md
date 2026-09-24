# 15-session validation protocol

## Purpose

Determine whether FINANCER V0 deserves a second paper-trading cycle and, only after that, a tiny real-money validation. Fifteen sessions are **not** enough to prove a durable edge.

## Pre-forward-test gate

Before Session 1:

1. Pull at least 6 months of USDINR futures history where available.
2. Freeze active strategy versions.
3. Verify no future bars leak into any feature or decision.
4. Set paper execution assumptions before seeing results.
5. Confirm all timestamps are normalized and session boundaries are correct.

## Forward-test rules

- Primary market: one active USDINR futures contract.
- No real orders.
- Record every candidate and rejection.
- One open position maximum in V0.
- Risk budget: 0.50% of current paper equity per trade.
- Stop for the day at -1.50% paper equity.
- Reject expected R:R below 1.35.
- Never edit an active strategy mid-session.
- Any proposed improvement becomes a new strategy version and must be tested separately.
- If both stop and target occur within the same OHLC bar and tick order is unknown, score the stop first.

## Daily report

Store:

- candidates generated / rejected / accepted
- trades closed
- net R
- net simulated P&L
- win rate
- average win R / average loss R
- profit factor
- max intraday drawdown
- strategy/regime breakdown
- data/API failures
- rule violations

## Initial pass criteria

These are screening thresholds, not guarantees:

- positive net result
- expectancy > +0.15R/trade
- profit factor >= 1.30
- max drawdown <= 4R
- average planned R:R >= 1.5
- zero look-ahead violations
- zero risk-rule violations
- zero unresolved data failures affecting a decision
- preferably >= 30 closed paper trades; if fewer, extend the forward test

## Decision after 15 sessions

**PASS:** continue paper testing with frozen strategy plus one controlled research branch.

**BORDERLINE:** no real money; extend another 15 sessions.

**FAIL:** no real money; diagnose whether the problem is strategy, regime detection, costs, data quality or overfitting.
