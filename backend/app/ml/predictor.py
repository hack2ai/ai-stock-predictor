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

    current_scale = max(abs(current_price), 1.0)
    error_ratio = result.metrics["rmse"] / current_scale
    validation_factor = min(1.0, result.validation_samples / 100.0)
    confidence = max(0.0, min(100.0, (1.0 - error_ratio) * validation_factor * 100.0))

    lower_bound = predicted_price - 1.96 * result.residual_std
    upper_bound = predicted_price + 1.96 * result.residual_std

    return {
        "current_price": round(current_price, 2),
        "predicted_next_close": round(predicted_price, 2),
        "prediction_interval": {
            "lower": round(max(0.0, lower_bound), 2),
            "upper": round(upper_bound, 2),
            "confidence_level": 95,
        },
        "expected_change_percent": round(change_pct, 2),
        "trend": trend,
        "confidence_score": round(confidence, 2),
        "metrics": result.metrics,
        "validation": {
            "method": "walk_forward_time_series",
            "samples": result.validation_samples,
        },
        "model": {
            "algorithm": "RandomForestRegressor",
            "random_state": 42,
        },
        "feature_importance": model_feature_importance(result),
        "disclaimer": "Educational AI analysis only. Forecasts are statistical estimates with uncertainty and are not financial advice.",
    }
