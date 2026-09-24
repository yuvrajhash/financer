from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from financer.config import get_settings
from financer.engine import FinancerEngine
from financer.journal import Journal
from financer.evaluation.metrics import calculate_metrics

app = typer.Typer(add_completion=False, help="FINANCER V0 paper-trading research CLI")


@app.command("init-db")
def init_db() -> None:
    s = get_settings()
    Journal(s.sqlite_path).init()
    typer.echo(f"Initialized {s.sqlite_path}")


@app.command("analyze-csv")
def analyze_csv(path: Path, min_score: float = 72.0) -> None:
    s = get_settings()
    df = pd.read_csv(path)
    dt_col = "datetime" if "datetime" in df.columns else "date"
    if dt_col in df.columns:
        df[dt_col] = pd.to_datetime(df[dt_col], utc=True)
        df = df.set_index(dt_col)
    engine = FinancerEngine(s, min_score=min_score)
    candidates = engine.evaluate(df)
    if not candidates:
        typer.echo("No setup")
        raise typer.Exit(0)
    for c in candidates:
        typer.echo(
            f"{c.signal.strategy} {c.signal.side.value} score={c.score.final:.1f} "
            f"RR={c.signal.rr:.2f} regime={c.regime.value} allowed={c.allowed}"
        )
        if c.rejection_reasons:
            typer.echo("  rejected: " + "; ".join(c.rejection_reasons))


@app.command("report")
def report() -> None:
    s = get_settings()
    journal = Journal(s.sqlite_path)
    journal.init()
    metrics = calculate_metrics(journal.trades_dataframe())
    for key, value in metrics.to_dict().items():
        typer.echo(f"{key}: {value}")


if __name__ == "__main__":
    app()
