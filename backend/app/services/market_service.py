from __future__ import annotations

import pandas as pd
import yfinance as yf
from fastapi import HTTPException


def fetch_market_history(ticker: str, period: str = "2y") -> pd.DataFrame:
    symbol = ticker.strip().upper()
    if not symbol:
        raise HTTPException(status_code=400, detail="Ticker is required.")

    try:
        data = yf.Ticker(symbol).history(period=period, auto_adjust=False)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Market data provider error: {exc}") from exc

    if data is None or data.empty:
        raise HTTPException(status_code=404, detail=f"No market data found for ticker '{symbol}'.")

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise HTTPException(status_code=502, detail=f"Market data is missing required fields: {', '.join(missing)}")

    return data[required].dropna().copy()
