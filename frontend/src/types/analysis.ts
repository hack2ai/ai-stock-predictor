export type Analysis = {
  ticker: string;
  latest_market: {
    close: number;
    volume: number;
  };
  history: {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }[];
  technical_indicators: Record<string, number | null>;
  prediction: {
    predicted_next_close: number;
    prediction_interval?: {
      lower: number;
      upper: number;
      confidence_level: number;
    };
    expected_change_percent: number;
    trend: "BULLISH" | "BEARISH" | "NEUTRAL";
    confidence_score: number;
    metrics: {
      mae: number;
      rmse: number;
      r2: number;
    };
    validation?: {
      method: string;
      samples: number;
    };
    model?: {
      algorithm: string;
      random_state: number;
    };
    feature_importance: Record<string, number>;
    disclaimer: string;
  };
};
