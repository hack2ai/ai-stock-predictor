from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Path, Query, Request, status

from app.api.schemas import StockAnalysisResponse
from app.core.cache import analysis_cache
from app.core.security import enforce_rate_limit
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


def _build_analysis(symbol: str, period: str, history_limit: int) -> StockAnalysisResponse:
    market_data = fetch_market_history(symbol, period=period)
    if market_data is None or market_data.empty:
        raise ValueError("No market data is available for this ticker.")

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

    return StockAnalysisResponse(
        ticker=symbol,
        period=period,
        data_points=len(market_data),
        latest_market={
            "open": round(float(latest["Open"]), 4),
            "high": round(float(latest["High"]), 4),
            "low": round(float(latest["Low"]), 4),
            "close": round(float(latest["Close"]), 4),
            "volume": int(latest["Volume"]),
        },
        technical_indicators=technical_indicators,
        prediction=prediction,
        history=history,
    )


@router.get("/{ticker}/analysis", response_model=StockAnalysisResponse)
def analyze_stock(
    request: Request,
    ticker: str = Path(..., min_length=1, max_length=20, pattern=r"^[A-Za-z0-9.^=\-]+$"),
    period: str = Query("2y", pattern="^(6mo|1y|2y|5y)$"),
    history_limit: int = Query(120, ge=30, le=500),
) -> StockAnalysisResponse:
    enforce_rate_limit(request)
    symbol = ticker.strip().upper()
    cache_key = f"analysis:{symbol}:{period}:{history_limit}"

    try:
        return analysis_cache.get_or_set(
            cache_key,
            lambda: _build_analysis(symbol, period, history_limit),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Market data or prediction service is temporarily unavailable.",
        ) from exc
