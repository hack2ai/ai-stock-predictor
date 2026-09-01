# AI Stock Intelligence Platform

A full-stack machine-learning platform for analyzing historical market data, generating technical indicators, and producing transparent next-session price estimates.

> **Educational use only.** Market analysis and model predictions are estimates, not financial advice.

## Features

- Stock and ticker search
- Historical OHLCV market data via yfinance
- Technical indicators: SMA, EMA, RSI, MACD and Bollinger Bands
- Volatility and return analysis
- Random Forest regression for next-close estimation
- MAE, RMSE and R² model metrics
- Feature-importance reporting
- Bullish, Bearish or Neutral trend classification
- Professional Next.js dashboard
- FastAPI REST API
- Automated tests and GitHub Actions CI
- Docker and Docker Compose support

## Architecture

```text
Market Data (yfinance)
        ↓
Market Data Service
        ↓
Feature Engineering + Technical Indicators
        ↓
Random Forest Training
        ↓
Prediction + Metrics + Feature Importance
        ↓
FastAPI REST API
        ↓
Next.js Intelligence Dashboard
```

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── indicators/
│   │   ├── ml/
│   │   └── services/
│   ├── tests/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   └── components/
│   └── package.json
├── .github/workflows/ci.yml
├── .env.example
├── docker-compose.yml
└── README.md
```

## API

### Health check

```text
GET /health
```

### Stock intelligence analysis

```text
GET /api/v1/stocks/{ticker}/analysis
```

Example:

```text
/api/v1/stocks/AAPL/analysis?period=2y&history_limit=120
```

The response includes latest market data, technical indicators, historical records, prediction estimates, confidence score, evaluation metrics and feature importance.

## Local Development

### Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install and run:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend API: `http://localhost:8000`

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`

Create frontend environment configuration when needed:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Docker

Start the application stack with:

```bash
docker compose up --build
```

## Testing

Backend tests:

```bash
cd backend
pytest tests -q
```

The GitHub Actions workflow runs backend tests and the frontend production build on pushes and pull requests.

## Production Notes

Before deploying publicly:

- Restrict CORS to trusted frontend domains.
- Add API rate limiting and caching for market-data requests.
- Replace simulated WebSocket prices with a licensed real-time market-data provider when presenting live data.
- Add walk-forward validation and prediction intervals before making stronger forecasting claims.
- Store model versions and evaluation results for reproducibility.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, Uvicorn |
| ML | scikit-learn, Random Forest |
| Data | Pandas, NumPy, yfinance |
| DevOps | Docker, Docker Compose, GitHub Actions |

## Author

**Pankaj (Tony) Kumar**

AI Engineer • Full Stack Developer • AI/ML Enthusiast

GitHub: https://github.com/hack2ai
LinkedIn: https://www.linkedin.com/in/pankaj-kumar-ab591a216
