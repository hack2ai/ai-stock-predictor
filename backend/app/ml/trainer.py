from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .features import build_feature_dataset, split_features_target


@dataclass
class TrainingResult:
    model: RandomForestRegressor
    latest_features: pd.DataFrame
    metrics: Dict[str, float]


def train_model(df: pd.DataFrame, test_ratio: float = 0.2) -> TrainingResult:
    data, feature_columns = build_feature_dataset(df)
    X, y = split_features_target(data, feature_columns)

    if len(X) < 50:
        raise ValueError("At least 50 usable observations are required for training.")

    split_index = max(1, int(len(X) * (1 - test_ratio)))
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    metrics: Dict[str, float] = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
        "r2": float(r2_score(y_test, predictions)),
    }

    return TrainingResult(
        model=model,
        latest_features=X.tail(1),
        metrics={key: round(value, 4) for key, value in metrics.items()},
    )


def model_feature_importance(result: TrainingResult) -> Dict[str, float]:
    columns = list(result.latest_features.columns)
    values = result.model.feature_importances_
    return {
        name: round(float(value), 4)
        for name, value in sorted(zip(columns, values), key=lambda item: item[1], reverse=True)
    }
