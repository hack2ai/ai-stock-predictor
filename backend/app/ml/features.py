from __future__ import annotations

from typing import List, Tuple

import pandas as pd

from app.indicators.technical_indicators import add_technical_indicators

FEATURE_COLUMNS = [
    "Open", "High", "Low", "Close", "Volume",
    "SMA_20", "SMA_50", "EMA_20", "RSI_14",
    "MACD", "MACD_SIGNAL", "MACD_HIST",
    "BB_UPPER", "BB_MIDDLE", "BB_LOWER",
    "RETURN_1D", "VOLATILITY_20", "HIGH_LOW_PCT",
    "CLOSE_LAG_1", "CLOSE_LAG_2", "CLOSE_LAG_3",
    "CLOSE_LAG_5", "CLOSE_LAG_10",
]


def build_feature_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    data = add_technical_indicators(df)

    for lag in (1, 2, 3, 5, 10):
        data[f"CLOSE_LAG_{lag}"] = data["Close"].shift(lag)

    data["TARGET_NEXT_CLOSE"] = data["Close"].shift(-1)
    data = data.dropna().reset_index(drop=True)

    if data.empty:
        raise ValueError("Not enough historical data to build the feature dataset.")

    return data, FEATURE_COLUMNS.copy()


def split_features_target(data: pd.DataFrame, feature_columns: List[str]):
    X = data[feature_columns].astype(float)
    y = data["TARGET_NEXT_CLOSE"].astype(float)
    return X, y
