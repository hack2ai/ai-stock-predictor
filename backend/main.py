from datetime import datetime
from typing import Dict, List
import asyncio
import json
import logging
import random
import time

from fastapi import FastAPI, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

from app.api.routes.analysis import router as analysis_router
from app.core.config import get_cors_origins
from ml_model.predict import predict_future

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_stock_intelligence")

app = FastAPI(
    title="AI Stock Intelligence API",
    version="1.1.0",
    description="Market analysis and machine-learning prediction API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_and_logging_middleware(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    duration_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "%s %s -> %s in %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(analysis_router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "ai-stock-intelligence-api"}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, ticker: str):
        await websocket.accept()
        self.active_connections.setdefault(ticker, []).append(websocket)

    def disconnect(self, websocket: WebSocket, ticker: str):
        connections = self.active_connections.get(ticker, [])
        if websocket in connections:
            connections.remove(websocket)

    async def broadcast(self, message: dict, ticker: str):
        for connection in list(self.active_connections.get(ticker, [])):
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                self.disconnect(connection, ticker)


manager = ConnectionManager()


@app.get("/api/historical/{ticker}")
def get_historical_data(ticker: str, period: str = "1y"):
    stock = yf.Ticker(ticker.strip().upper())
    hist = stock.history(period=period)
    if hist.empty:
        return {"error": "No data found for this ticker."}

    hist = hist.reset_index()
    hist["Date"] = hist["Date"].dt.strftime("%Y-%m-%d")
    records = hist[["Date", "Open", "High", "Low", "Close", "Volume"]].to_dict(orient="records")
    return {"ticker": ticker.upper(), "data": records}


@app.get("/api/predict/{ticker}")
def get_predictions(ticker: str, days: int = Query(7, ge=1, le=30)):
    predictions, metrics = predict_future(ticker.strip().upper(), days=days)
    return {"ticker": ticker.upper(), "predictions": predictions, "metrics": metrics}


@app.websocket("/ws/stock/{ticker}")
async def websocket_endpoint(websocket: WebSocket, ticker: str):
    symbol = ticker.strip().upper()
    await manager.connect(websocket, symbol)
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        current_price = float(hist["Close"].iloc[-1]) if not hist.empty else 150.0

        while True:
            await asyncio.sleep(1)
            change = current_price * random.uniform(-0.001, 0.001)
            current_price += change
            await manager.broadcast({
                "ticker": symbol,
                "price": round(current_price, 2),
                "time": datetime.now().strftime("%H:%M:%S"),
                "change": round(change, 2),
                "change_percent": round((change / (current_price - change)) * 100, 3),
                "source": "simulation",
            }, symbol)
    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
