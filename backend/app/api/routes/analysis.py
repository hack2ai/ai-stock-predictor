from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Path, Query, Request, status

from app.api.schemas import AIExplanation, StockAnalysisResponse
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


def generate_ai_explanation(
    ticker: str,
    prediction: Dict[str, Any],
    technical_indicators: Dict[str, Any],
) -> AIExplanation:
    current_price = float(prediction.get("current_price", 0.0))
    predicted_price = float(prediction.get("predicted_next_close", current_price))
    expected_change = float(prediction.get("expected_change_percent", 0.0))
    trend = str(prediction.get("trend", "NEUTRAL")).upper()
    confidence = float(prediction.get("confidence_score", 0.0))

    signals: List[str] = []
    rsi = technical_indicators.get("rsi_14")
    macd = technical_indicators.get("macd")
    macd_signal = technical_indicators.get("macd_signal")
    sma_20 = technical_indicators.get("sma_20")
    sma_50 = technical_indicators.get("sma_50")

    if rsi is not None:
        if rsi >= 70:
            signals.append(f"RSI is {rsi:.1f}, indicating potentially overbought conditions.")
        elif rsi <= 30:
            signals.append(f"RSI is {rsi:.1f}, indicating potentially oversold conditions.")
        else:
            signals.append(f"RSI is {rsi:.1f}, which is within a neutral range.")

    if macd is not None and macd_signal is not None:
        if macd > macd_signal:
            signals.append("MACD is above its signal line, supporting positive momentum.")
        else:
            signals.append("MACD is below its signal line, suggesting weaker momentum.")

    if sma_20 is not None and sma_50 is not None:
        if sma_20 > sma_50:
            signals.append("The 20-day SMA is above the 50-day SMA, supporting the broader trend.")
        else:
            signals.append("The 20-day SMA is below the 50-day SMA, which may indicate trend weakness.")

    if not signals:
        signals.append("Technical indicator data is limited, so the explanation is based mainly on the model prediction.")

    if trend == "BULLISH" or expected_change > 0:
        summary = (
            f"The model expects {ticker} to move from approximately {current_price:.2f} "
            f"to {predicted_price:.2f}, an estimated change of {expected_change:.2f}%"
            ". The current signal is positive, but market conditions can change quickly."
        )
        outlook: Literal["BULLISH", "BEARISH", "NEUTRAL"] = "BULLISH"
    elif trend == "BEARISH" or expected_change < 0:
        summary = (
            f"The model expects {ticker} to move from approximately {current_price:.2f} "
            f"to {predicted_price:.2f}, an estimated change of {expected_change:.2f}%"
            ". The current signal is negative, so risk management is important."
        )
        outlook = "BEARISH"
    else:
        summary = (
            f"The model expects limited short-term movement for {ticker}, with a predicted next close "
            f"near {predicted_price:.2f}. Current indicators do not show a strong directional signal."
        )
        outlook = "NEUTRAL"

    risk_note = (
        "This explanation combines the current model prediction with technical indicators. "
        "Unexpected market news, earnings, and macroeconomic events can make actual prices differ from the prediction."
    )

    return AIExplanation(
        summary=summary,
        outlook=outlook,
        confidence=round(max(0.0, min(confidence, 100.0)), 2),
        key_signals=signals,
        risk_note=risk_note,
        disclaimer="Educational information only; this is not financial advice or a guarantee of future market performance.",
    )


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

    ai_explanation = generate_ai_explanation(
        symbol,
        prediction,
        technical_indicators,
    )

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
        ai_explanation=ai_explanation,
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
