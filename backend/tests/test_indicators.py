import pandas as pd

from app.indicators.technical_indicators import add_technical_indicators


def test_add_technical_indicators_creates_expected_columns():
    df = pd.DataFrame({
        "Open": range(1, 80),
        "High": range(2, 81),
        "Low": range(0, 79),
        "Close": range(1, 80),
        "Volume": [1000] * 79,
    })

    result = add_technical_indicators(df)

    for column in ["SMA_20", "SMA_50", "RSI_14", "MACD", "BB_UPPER", "VOLATILITY_20"]:
        assert column in result.columns

    assert len(result) == len(df)
