from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .trainer import model_feature_importance, train_model


def predict_next_close(df: pd.DataFrame) -> Dict[str, Any]:
    result = train_model(df)
    predicted_price = float(result.model.predict(result.latest_features)[0])
    current_price = float(df["Close"].iloc[-1])
    change_pct = ((predicted_price - current_price) / current_price) * 100 if current_price else 0.0

    if change_pct > 1:
        trend = "BULLISH"
    elif change_pct < -1:
        trend = "BEARISH"
    else:
        trend = "NEUTRAL"

    confidence = max(0.0, min(100.0, 100.0 - result.metrics["rmse"] / max(abs(current_price), 1.0) * 100.0))

    return {
        "current_price": round(current_price, 2),
        "predicted_next_close": round(predicted_price, 2),
        "expected_change_percent": round(change_pct, 2),
        "trend": trend,
        "confidence_score": round(confidence, 2),
        "metrics": result.metrics,
        "feature_importance": model_feature_importance(result),
        "disclaimer": "Educational AI analysis only. Market predictions are estimates and not financial advice.",
    }
