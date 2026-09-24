from __future__ import annotations

import numpy as np
import pandas as pd


REQUIRED_OHLC = {"open", "high", "low", "close"}


def validate_ohlc(df: pd.DataFrame) -> None:
    missing = REQUIRED_OHLC - set(df.columns)
    if missing:
        raise ValueError(f"Missing OHLC columns: {sorted(missing)}")


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    validate_ohlc(df)
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50.0)


def adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    validate_ohlc(df)
    up_move = df["high"].diff()
    down_move = -df["low"].diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index)

    atr_series = atr(df, period)
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False, min_periods=period).mean() / atr_series
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False, min_periods=period).mean() / atr_series
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / period, adjust=False, min_periods=period).mean().fillna(0.0)


def rolling_percentile_rank(series: pd.Series, window: int = 100) -> pd.Series:
    def rank_last(values: np.ndarray) -> float:
        if len(values) == 0 or np.isnan(values[-1]):
            return np.nan
        valid = values[~np.isnan(values)]
        if len(valid) == 0:
            return np.nan
        return float((valid <= values[-1]).sum() / len(valid) * 100)

    return series.rolling(window, min_periods=max(20, window // 4)).apply(rank_last, raw=True)


def add_core_features(df: pd.DataFrame) -> pd.DataFrame:
    validate_ohlc(df)
    out = df.copy()
    out["ema20"] = ema(out["close"], 20)
    out["ema50"] = ema(out["close"], 50)
    out["atr14"] = atr(out, 14)
    out["rsi14"] = rsi(out["close"], 14)
    out["adx14"] = adx(out, 14)
    out["atr_pct"] = rolling_percentile_rank(out["atr14"], 100)
    out["sma20"] = out["close"].rolling(20).mean()
    out["std20"] = out["close"].rolling(20).std(ddof=0)
    out["range20_high"] = out["high"].shift(1).rolling(20).max()
    out["range20_low"] = out["low"].shift(1).rolling(20).min()
    if "volume" in out.columns:
        out["volume20"] = out["volume"].rolling(20).mean()
    else:
        out["volume"] = 0.0
        out["volume20"] = 0.0
    return out
