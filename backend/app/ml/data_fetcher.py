import yfinance as yf
import pandas as pd

TICKER_MAP = {
    "NIFTY 50": "^NSEI",
    "NIFTY50": "^NSEI",
    "INFITY 50": "^NSEI",
    "INFITY 50 INDEX": "^NSEI",
    "NIFTY 50 INDEX": "^NSEI",
    "S&P 500": "^GSPC",
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW JONES": "^DJI"
}

def clean_ticker(ticker: str) -> str:
    t = ticker.upper().strip()
    return TICKER_MAP.get(t, t)

def fetch_historical_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical stock data for the given ticker.
    """
    stock = yf.Ticker(clean_ticker(ticker))
    df = stock.history(period=period, interval=interval)
    
    if df.empty:
        return pd.DataFrame()
        
    df.reset_index(inplace=True)
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    return df

def fetch_realtime_data(ticker: str) -> dict:
    """
    Fetch the most recent data point for real-time updates.
    Using period '1d' and interval '1m' to get the latest minute data.
    """
    stock = yf.Ticker(clean_ticker(ticker))
    df = stock.history(period="1d", interval="1m")
    
    if df.empty:
        return {}
        
    latest = df.iloc[-1]
    return {
        "timestamp": latest.name.isoformat(),
        "open": float(latest['Open']),
        "high": float(latest['High']),
        "low": float(latest['Low']),
        "close": float(latest['Close']),
        "volume": int(latest['Volume'])
    }
