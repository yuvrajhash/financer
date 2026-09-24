from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import typer

from financer.backtest.runner import BacktestRunner
from financer.config import get_settings
from financer.data.contracts import select_nearest_future
from financer.data.twelve_data import TwelveDataClient
from financer.data.zerodha import ZerodhaDataClient
from financer.engine import FinancerEngine
from financer.evaluation.metrics import calculate_metrics
from financer.evaluation.report import render_backtest_report
from financer.journal import Journal
from financer.scoring.engine import ContextScores

app = typer.Typer(add_completion=False, help="FINANCER V0 paper-trading research CLI")


def _load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    dt_col = "datetime" if "datetime" in df.columns else "date"
    if dt_col in df.columns:
        df[dt_col] = pd.to_datetime(df[dt_col], utc=True)
        df = df.set_index(dt_col)
    return df.sort_index()


@app.command("init-db")
def init_db() -> None:
    s = get_settings()
    Journal(s.sqlite_path).init()
    typer.echo(f"Initialized {s.sqlite_path}")


@app.command("kite-login-url")
def kite_login_url() -> None:
    """Print the official Zerodha login URL for today's Kite session."""
    s = get_settings()
    typer.echo(login_url(s.kite_api_key))


@app.command("kite-exchange-token")
def kite_exchange_token(request_token: str) -> None:
    """Exchange the short-lived redirect request_token for today's access token.

    The API secret stays local in .env. The returned access token is intentionally
    printed only to the local terminal; do not paste it into GitHub or chat.
    """
    s = get_settings()
    session = exchange_request_token(s.kite_api_key, s.kite_api_secret, request_token)
    access_token = session.get("access_token")
    if not access_token:
        raise typer.BadParameter("Kite did not return an access_token")
    typer.echo("KITE_ACCESS_TOKEN=" + access_token)


@app.command("analyze-csv")
def analyze_csv(path: Path, min_score: float = 72.0) -> None:
    s = get_settings()
    df = _load_csv(path)
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


@app.command("fetch-kite-usdinr")
def fetch_kite_usdinr(
    output: Path = Path("data/usdinr_current_5m.csv"),
    days: int = 90,
    interval: str = "5minute",
) -> None:
    """Fetch the nearest live USDINR futures contract from Kite.

    Important: Kite does not provide intraday candles for expired futures. This command
    therefore downloads only the currently live contract and should be rerun daily so
    FINANCER builds its own continuous intraday archive over time.
    """
    s = get_settings()
    client = ZerodhaDataClient(s.kite_api_key, s.kite_access_token)
    instruments = client.instruments("CDS")
    contract = select_nearest_future(instruments, "USDINR")

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=min(max(days, 1), 100))
    df = client.historical(
        contract.instrument_token,
        from_date=start,
        to_date=end,
        interval=interval,
        oi=True,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output)
    typer.echo(
        f"Saved {len(df)} rows for {contract.tradingsymbol} "
        f"(expiry {contract.expiry}, lot {contract.lot_size}, tick {contract.tick_size}) "
        f"to {output}"
    )


@app.command("fetch-spot-usdinr")
def fetch_spot_usdinr(
    output: Path = Path("data/usdinr_spot_proxy_5m.csv"),
    interval: str = "5min",
    outputsize: int = 5000,
) -> None:
    """Fetch USD/INR spot as a research proxy only."""
    s = get_settings()
    client = TwelveDataClient(s.twelve_data_api_key)
    df = client.time_series("USD/INR", interval=interval, outputsize=outputsize)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output)
    typer.echo(f"Saved {len(df)} USD/INR spot proxy rows to {output}")


@app.command("backtest-csv")
def backtest_csv(
    path: Path,
    source_label: str = "nse-usdinr-current-future",
    min_score: float = 72.0,
    warmup_bars: int = 120,
) -> None:
    s = get_settings()
    df = _load_csv(path)
    runner = BacktestRunner(s, min_score=min_score, warmup_bars=warmup_bars)
    result = runner.run(
        df,
        context=ContextScores(),
        source_label=source_label,
    )
    typer.echo(render_backtest_report(result))


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
