from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

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
    residual_std: float
    validation_samples: int


def _create_model() -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )


def _walk_forward_predictions(X: pd.DataFrame, y: pd.Series, folds: int = 5):
    minimum_train_size = max(40, len(X) // (folds + 1))
    remaining = len(X) - minimum_train_size
    step = max(1, remaining // folds)
    predictions, actuals = [], []

    for split in range(minimum_train_size, len(X), step):
        end = min(split + step, len(X))
        if end <= split:
            continue
        model = _create_model()
        model.fit(X.iloc[:split], y.iloc[:split])
        fold_predictions = model.predict(X.iloc[split:end])
        predictions.extend(fold_predictions.tolist())
        actuals.extend(y.iloc[split:end].tolist())

    return np.asarray(actuals), np.asarray(predictions)


def train_model(df: pd.DataFrame, test_ratio: float = 0.2) -> TrainingResult:
    data, feature_columns = build_feature_dataset(df)
    X, y = split_features_target(data, feature_columns)

    if len(X) < 50:
        raise ValueError("At least 50 usable observations are required for training.")

    split_index = max(40, int(len(X) * (1 - test_ratio)))
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    model = _create_model()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    residuals = y_test.to_numpy() - predictions
    walk_actual, walk_pred = _walk_forward_predictions(X, y)

    evaluation_actual = walk_actual if len(walk_actual) else y_test.to_numpy()
    evaluation_pred = walk_pred if len(walk_pred) else predictions

    metrics: Dict[str, float] = {
        "mae": float(mean_absolute_error(evaluation_actual, evaluation_pred)),
        "rmse": float(np.sqrt(mean_squared_error(evaluation_actual, evaluation_pred))),
        "r2": float(r2_score(evaluation_actual, evaluation_pred)),
    }

    return TrainingResult(
        model=model,
        latest_features=X.tail(1),
        metrics={key: round(value, 4) for key, value in metrics.items()},
        residual_std=float(np.std(residuals, ddof=1)) if len(residuals) > 1 else 0.0,
        validation_samples=int(len(evaluation_actual)),
    )


def model_feature_importance(result: TrainingResult) -> Dict[str, float]:
    columns = list(result.latest_features.columns)
    values = result.model.feature_importances_
    return {
        name: round(float(value), 4)
        for name, value in sorted(zip(columns, values), key=lambda item: item[1], reverse=True)
    }
