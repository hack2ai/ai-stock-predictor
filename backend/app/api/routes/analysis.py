from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from fastapi import APIRouter, Query

from app.indicators.technical_indicators import add_technical_indicators
from app.ml.predictor import predict_next_close
from app.services.market_service import fetch_market_history

router = APIRouter(prefix="/api/v1/stocks", tags=["Stock Analysis"])


def _clean(value: Any) -> Any:
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if pd.isna(value):
        return None
    return value


@router.get("/{ticker}/analysis")
def analyze_stock(
    ticker: str,
    period: str = Query("2y", pattern="^(6mo|1y|2y|5y)$"),
    history_limit: int = Query(120, ge=30, le=500),
) -> Dict[str, Any]:
    symbol = ticker.strip().upper()
    market_data = fetch_market_history(symbol, period=period)
    indicator_data = add_technical_indicators(market_data)
    prediction = predict_next_close(market_data)

    latest = indicator_data.iloc[-1]
    history: List[Dict[str, Any]] = []
    for index, row in indicator_data.tail(history_limit).iterrows():
        history.append({
            "date": str(index.date()) if hasattr(index, "date") else str(index),
            "open": round(float(row["Open"]), 4),
            "high": round(float(row["High"]), 4),
            "low": round(float(row["Low"]), 4),
            "close": round(float(row["Close"]), 4),
            "volume": int(row["Volume"]),
        })

    technical_indicators = {
        key.lower(): _clean(round(float(latest[key]), 4)) if not pd.isna(latest[key]) else None
        for key in [
            "SMA_20", "SMA_50", "EMA_20", "RSI_14", "MACD",
            "MACD_SIGNAL", "MACD_HIST", "BB_UPPER", "BB_MIDDLE",
            "BB_LOWER", "VOLATILITY_20",
        ]
    }

    return {
        "ticker": symbol,
        "period": period,
        "data_points": len(market_data),
        "latest_market": {
            "open": round(float(latest["Open"]), 4),
            "high": round(float(latest["High"]), 4),
            "low": round(float(latest["Low"]), 4),
            "close": round(float(latest["Close"]), 4),
            "volume": int(latest["Volume"]),
        },
        "technical_indicators": technical_indicators,
        "prediction": prediction,
        "history": history,
    }
