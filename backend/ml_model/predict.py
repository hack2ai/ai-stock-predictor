from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd
from datetime import timedelta

from .data_fetcher import fetch_data, preprocess_data

def train_and_predict(ticker: str, days: int = 7):
    # Fetch data
    df_raw = fetch_data(ticker, period="2y")
    X, y, df, features = preprocess_data(df_raw)
    
    # Train-test split (80-20)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Train Random Forest
    rf = RandomForestRegressor(n_estimators=50, random_state=42)
    rf.fit(X_train, y_train)
    
    # Evaluate
    y_pred_rf = rf.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred_rf)
    mse = mean_squared_error(y_test, y_pred_rf)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred_rf)
    
    metrics = {
        "MAE": round(mae, 2),
        "MSE": round(mse, 2),
        "RMSE": round(rmse, 2),
        "R2": round(r2, 4)
    }
    
    # Predict future 'days'
    future_predictions = []
    
    # Start with the last known window
    last_window = X[-1].reshape(1, -1)
    
    current_date = df['Date'].iloc[-1]
    
    for _ in range(days):
        # Predict next day using RF
        next_price = rf.predict(last_window)[0]
        
        # Advance date (skipping weekends roughly)
        current_date += timedelta(days=1)
        if current_date.weekday() >= 5: # Saturday or Sunday
            current_date += timedelta(days=(7 - current_date.weekday()))
            
        future_predictions.append({
            "Date": current_date.strftime('%Y-%m-%d'),
            "Predicted_Price": round(next_price, 2)
        })
        
        new_window = np.roll(last_window, 1)
        new_window[0, 0] = next_price
        last_window = new_window
        
    return future_predictions, metrics

def predict_future(ticker: str, days: int = 7):
    return train_and_predict(ticker, days)
