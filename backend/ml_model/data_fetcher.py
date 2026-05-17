import yfinance as yf
import pandas as pd
import numpy as np

def fetch_data(ticker: str, period: str = "5y"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    if df.empty:
        raise ValueError(f"No data found for ticker {ticker}")
    df = df.reset_index()
    return df

def preprocess_data(df: pd.DataFrame):
    # We will predict the 'Close' price based on historical 'Close' prices
    df = df[['Date', 'Close']].copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Feature engineering: Use past N days to predict next day
    window_size = 10
    
    for i in range(1, window_size + 1):
        df[f'Close_lag_{i}'] = df['Close'].shift(i)
        
    df = df.dropna()
    
    features = [f'Close_lag_{i}' for i in range(1, window_size + 1)]
    X = df[features].values
    y = df['Close'].values
    
    return X, y, df, features
