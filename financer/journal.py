from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from financer.models import PaperTrade, TradeCandidate


SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  generated_at TEXT NOT NULL,
  strategy TEXT NOT NULL,
  strategy_version TEXT NOT NULL,
  side TEXT NOT NULL,
  entry REAL NOT NULL,
  stop REAL NOT NULL,
  target REAL NOT NULL,
  regime TEXT NOT NULL,
  final_score REAL NOT NULL,
  allowed INTEGER NOT NULL,
  rejection_reasons TEXT NOT NULL,
  reasons TEXT NOT NULL,
  ai_review TEXT
);

CREATE TABLE IF NOT EXISTS paper_trades (
  id TEXT PRIMARY KEY,
  strategy TEXT NOT NULL,
  strategy_version TEXT NOT NULL,
  side TEXT NOT NULL,
  opened_at TEXT NOT NULL,
  closed_at TEXT,
  entry REAL NOT NULL,
  exit_price REAL,
  stop REAL NOT NULL,
  target REAL NOT NULL,
  quantity INTEGER NOT NULL,
  score REAL NOT NULL,
  pnl REAL NOT NULL,
  r_multiple REAL NOT NULL,
  exit_reason TEXT,
  status TEXT NOT NULL
);
"""


class Journal:
    def __init__(self, path: str):
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def record_candidate(self, c: TradeCandidate) -> None:
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO candidates
                (generated_at,strategy,strategy_version,side,entry,stop,target,regime,final_score,
                 allowed,rejection_reasons,reasons,ai_review)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    c.signal.generated_at.isoformat(), c.signal.strategy, c.signal.strategy_version,
                    c.signal.side.value, c.signal.entry, c.signal.stop, c.signal.target, c.regime.value,
                    c.score.final, int(c.allowed), json.dumps(c.rejection_reasons),
                    json.dumps(c.signal.reasons), c.ai_review,
                ),
            )

    def record_trade(self, t: PaperTrade) -> None:
        with self.connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO paper_trades
                (id,strategy,strategy_version,side,opened_at,closed_at,entry,exit_price,stop,target,
                 quantity,score,pnl,r_multiple,exit_reason,status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    t.id, t.strategy, t.strategy_version, t.side.value, t.opened_at.isoformat(),
                    t.closed_at.isoformat() if t.closed_at else None, t.entry, t.exit_price, t.stop,
                    t.target, t.quantity, t.score, t.pnl, t.r_multiple, t.exit_reason, t.status,
                ),
            )

    def trades_dataframe(self):
        import pandas as pd
        with self.connect() as conn:
            return pd.read_sql_query("SELECT * FROM paper_trades ORDER BY opened_at", conn)
