from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    kite_api_key: str = ""
    kite_access_token: str = ""
    twelve_data_api_key: str = ""
    fred_api_key: str = ""

    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-luna"
    enable_ai_review: bool = False
    enable_ai_web_search: bool = False
    ai_review_min_score: float = 78.0

    paper_starting_capital: float = 100_000.0
    max_risk_per_trade_pct: float = 0.50
    max_daily_loss_pct: float = 1.50
    max_open_positions: int = 1

    paper_tick_size: float = 0.0025
    paper_lot_size: int = 1000
    paper_slippage_ticks: int = 1
    paper_round_trip_cost: float = 40.0

    sqlite_path: str = "financer.sqlite3"


@lru_cache
def get_settings() -> Settings:
    return Settings()
