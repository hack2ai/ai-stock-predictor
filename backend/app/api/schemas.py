from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class MarketSnapshot(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: int = Field(ge=0)


class HistoricalCandle(MarketSnapshot):
    date: str


class TechnicalIndicators(BaseModel):
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_20: Optional[float] = None
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    volatility_20: Optional[float] = None


class ModelMetrics(BaseModel):
    mae: float = Field(ge=0)
    rmse: float = Field(ge=0)
    r2: float


class PredictionResult(BaseModel):
    current_price: float
    predicted_next_close: float
    expected_change_percent: float
    trend: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    confidence_score: float = Field(ge=0, le=100)
    metrics: ModelMetrics
    feature_importance: Dict[str, float]
    disclaimer: str


class AIExplanation(BaseModel):
    summary: str
    outlook: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    confidence: float = Field(ge=0, le=100)
    key_signals: List[str]
    risk_note: str
    disclaimer: str


class StockAnalysisResponse(BaseModel):
    ticker: str = Field(min_length=1, max_length=20)
    period: Literal["6mo", "1y", "2y", "5y"]
    data_points: int = Field(ge=1)
    latest_market: MarketSnapshot
    technical_indicators: TechnicalIndicators
    prediction: PredictionResult
    ai_explanation: AIExplanation
    history: List[HistoricalCandle]
