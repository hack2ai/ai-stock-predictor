import asyncio
import json
import random
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.ml.data_fetcher import fetch_historical_data, fetch_realtime_data
from app.ml.train import StockPredictor

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictors = {}

@app.get("/")
def root():
    return {"message": "Stock Predictor API is running"}


@app.get("/api/models")
def list_models():
    return {"trained_tickers": list(predictors.keys())}

@app.get("/api/stock/{ticker}")
async def get_historical_data(ticker: str):
    try:
        df = fetch_historical_data(ticker, period="1y", interval="1d")
        if df.empty:
            return {"error": f"No data found for ticker: {ticker}"}

        records = df.to_dict(orient="records")
        for r in records:
           
            if hasattr(r["Date"], "isoformat"):
                r["Date"] = r["Date"].isoformat()

        return {"ticker": ticker, "data": records}

    except Exception as e:
        return {"error": str(e)}

@app.post("/api/train/{ticker}")
async def train_model(ticker: str):
    try:
        df = fetch_historical_data(ticker, period="2y", interval="1d")
        if df.empty:
            return {"error": "Insufficient data for training"}

        predictor = StockPredictor()
        success = predictor.train(df)

        if success:
            predictors[ticker] = predictor
            return {
                "message": f"Model trained successfully for {ticker}",
                "metrics": predictor.metrics,
            }
        return {"error": "Training failed"}

    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws/stock/{ticker}")
async def websocket_endpoint(websocket: WebSocket, ticker: str):
    await websocket.accept()
    print(f"[WS] Client connected: {ticker}")

    current_data = fetch_realtime_data(ticker)
    if not current_data:
        current_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "open": 150.0,
            "high": 152.0,
            "low": 149.0,
            "close": 151.0,
            "volume": 1_000_000,
        }

    try:
        while True:
            predictor = predictors.get(ticker)

            tick = dict(current_data)
            noise = random.uniform(-0.5, 0.5)
            tick["close"] = round(tick["close"] + noise, 4)
            tick["high"] = round(max(tick["high"], tick["close"]), 4)
            tick["low"] = round(min(tick["low"], tick["close"]), 4)
            tick["timestamp"] = datetime.now(timezone.utc).isoformat()
            current_data = tick

            prediction = 0.0
            if predictor and predictor.is_trained:
                try:
                    prediction = predictor.predict(tick)
                except Exception as e:
                    print(f"[WS] Prediction error: {e}")

            payload = {
                "ticker": ticker,
                "current": tick,
                "prediction": prediction,
                "is_model_trained": predictor is not None and predictor.is_trained,
            }

            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print(f"[WS] Client disconnected: {ticker}")
    except Exception as e:
        print(f"[WS] Error: {e}")
        await websocket.close()