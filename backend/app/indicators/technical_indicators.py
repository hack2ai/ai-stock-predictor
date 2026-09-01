from __future__ import annotations

import numpy as np
import pandas as pd


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add common technical indicators without mutating the input frame."""
    data = df.copy()

    required = {"Open", "High", "Low", "Close", "Volume"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    close = pd.to_numeric(data["Close"], errors="coerce")
    high = pd.to_numeric(data["High"], errors="coerce")
    low = pd.to_numeric(data["Low"], errors="coerce")

    data["SMA_20"] = close.rolling(20, min_periods=20).mean()
    data["SMA_50"] = close.rolling(50, min_periods=50).mean()
    data["EMA_12"] = close.ewm(span=12, adjust=False).mean()
    data["EMA_26"] = close.ewm(span=26, adjust=False).mean()
    data["EMA_20"] = close.ewm(span=20, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    data["RSI_14"] = 100 - (100 / (1 + rs))

    data["MACD"] = data["EMA_12"] - data["EMA_26"]
    data["MACD_SIGNAL"] = data["MACD"].ewm(span=9, adjust=False).mean()
    data["MACD_HIST"] = data["MACD"] - data["MACD_SIGNAL"]

    rolling_std = close.rolling(20, min_periods=20).std()
    data["BB_MIDDLE"] = data["SMA_20"]
    data["BB_UPPER"] = data["SMA_20"] + 2 * rolling_std
    data["BB_LOWER"] = data["SMA_20"] - 2 * rolling_std

    data["RETURN_1D"] = close.pct_change()
    data["VOLATILITY_20"] = data["RETURN_1D"].rolling(20, min_periods=20).std() * np.sqrt(252)
    data["HIGH_LOW_PCT"] = (high - low) / close.replace(0, np.nan)

    return data
