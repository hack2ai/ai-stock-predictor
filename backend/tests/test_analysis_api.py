import pandas as pd
from fastapi.testclient import TestClient

from main import app
import app.api.routes.analysis as analysis_module


client = TestClient(app)


def sample_market_data() -> pd.DataFrame:
    index = pd.date_range("2025-01-01", periods=80, freq="D")
    return pd.DataFrame(
        {
            "Open": [100 + i for i in range(80)],
            "High": [101 + i for i in range(80)],
            "Low": [99 + i for i in range(80)],
            "Close": [100 + i for i in range(80)],
            "Volume": [1_000_000] * 80,
        },
        index=index,
    )


def test_analysis_endpoint_returns_typed_response(monkeypatch):
    monkeypatch.setattr(analysis_module, "fetch_market_history", lambda *args, **kwargs: sample_market_data())
    monkeypatch.setattr(
        analysis_module,
        "predict_next_close",
        lambda data: {
            "current_price": 179.0,
            "predicted_next_close": 181.5,
            "expected_change_percent": 1.4,
            "trend": "BULLISH",
            "confidence_score": 72.5,
            "metrics": {"mae": 2.1, "rmse": 3.4, "r2": 0.82},
            "feature_importance": {"close": 0.45, "rsi": 0.25},
            "disclaimer": "Educational use only.",
        },
    )

    response = client.get("/api/v1/stocks/AAPL/analysis?period=1y&history_limit=30")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "AAPL"
    assert payload["period"] == "1y"
    assert payload["data_points"] == 80
    assert len(payload["history"]) == 30
    assert payload["prediction"]["trend"] == "BULLISH"
    assert 0 <= payload["prediction"]["confidence_score"] <= 100


def test_analysis_rejects_invalid_period():
    response = client.get("/api/v1/stocks/AAPL/analysis?period=10y")
    assert response.status_code == 422


def test_analysis_rejects_invalid_history_limit():
    response = client.get("/api/v1/stocks/AAPL/analysis?history_limit=5")
    assert response.status_code == 422
