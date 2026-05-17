import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

class StockPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.metrics = {}

    def prepare_data(self, df: pd.DataFrame):
        """
        Prepare dataframe for training.
        We will predict the 'Close' price of the next period.
        """
        # Create the target variable: next period's close price
        df['Target'] = df['Close'].shift(-1)
        df.dropna(inplace=True)

        features = ['Open', 'High', 'Low', 'Close', 'Volume']
        X = df[features]
        y = df['Target']

        return X, y

    def train(self, df: pd.DataFrame):
        if df.empty or len(df) < 50:
            return False

        X, y = self.prepare_data(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate
        predictions = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))

        self.metrics = {
            "mae": round(mae, 4),
            "rmse": round(rmse, 4)
        }
        return True

    def predict(self, current_data: dict) -> float:
        """
        Predict the next close price based on current tick data.
        """
        if not self.is_trained:
            return 0.0

        features = ['open', 'high', 'low', 'close', 'volume']
        X_input = pd.DataFrame([[current_data[f] for f in features]], columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        prediction = self.model.predict(X_input)
        return float(prediction[0])
