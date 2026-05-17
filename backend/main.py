from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import json
import asyncio
import random
from typing import List, Dict
from datetime import datetime

from ml_model.predict import predict_future

app = FastAPI(title="Stock Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, ticker: str):
        await websocket.accept()
        if ticker not in self.active_connections:
            self.active_connections[ticker] = []
        self.active_connections[ticker].append(websocket)

    def disconnect(self, websocket: WebSocket, ticker: str):
        if ticker in self.active_connections:
            self.active_connections[ticker].remove(websocket)

    async def broadcast(self, message: dict, ticker: str):
        if ticker in self.active_connections:
            for connection in self.active_connections[ticker]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    pass

manager = ConnectionManager()

@app.get("/api/historical/{ticker}")
def get_historical_data(ticker: str, period: str = "1y"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
             return {"error": "No data found for this ticker."}
        
        hist = hist.reset_index()
        # Ensure we only keep date part for frontend simplicity if it's daily data
        hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
        
        records = hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient='records')
        return {"ticker": ticker, "data": records}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/predict/{ticker}")
def get_predictions(ticker: str, days: int = Query(7, ge=1, le=30)):
    try:
        predictions, metrics = predict_future(ticker, days=days)
        return {"ticker": ticker, "predictions": predictions, "metrics": metrics}
    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws/stock/{ticker}")
async def websocket_endpoint(websocket: WebSocket, ticker: str):
    await manager.connect(websocket, ticker)
    try:
        # Get initial price to start simulating
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        current_price = 150.0 # Default fallback
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]

        while True:
            await asyncio.sleep(1) # Send update every 1 second
            # Simulate real-time price fluctuation (random walk)
            change = current_price * random.uniform(-0.001, 0.001) # +/- 0.1% change
            current_price += change
            
            now = datetime.now().strftime('%H:%M:%S')
            
            data = {
                "ticker": ticker,
                "price": round(current_price, 2),
                "time": now,
                "change": round(change, 2),
                "change_percent": round((change / (current_price - change)) * 100, 3)
            }
            await manager.broadcast(data, ticker)
    except WebSocketDisconnect:
        manager.disconnect(websocket, ticker)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
