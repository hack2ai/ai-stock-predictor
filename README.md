# Real-Time AI Stock Predictor

> A full-stack machine-learning application for exploring historical market data, simulated real-time price updates, and short-horizon price predictions through an interactive web dashboard.

[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![WebSockets](https://img.shields.io/badge/WebSockets-Realtime-0F172A?style=for-the-badge)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

## Overview

This project combines a **Next.js frontend** with a **FastAPI + Python machine-learning backend**. Historical market data is retrieved through `yfinance`, features are prepared with Python data tooling, and a Random Forest regression model is used to generate experimental short-term predictions.

The interface presents historical and predicted values through interactive charts while WebSockets provide the real-time update channel.

> **Disclaimer:** This is an educational machine-learning project, not financial advice. Model predictions are experimental and should not be used as a basis for investment decisions.

## Architecture

```text
                 Market Data
                     │
                  yfinance
                     │
                     ▼
              Python Data Layer
                     │
              Feature Preparation
                     │
                     ▼
            Random Forest Regressor
                     │
             Prediction Service
                     │
              FastAPI + WebSocket
                     │
                     ▼
            Next.js / React UI
                     │
               Recharts Dashboard
```

## Key Features

- Historical market-data ingestion
- Random Forest regression model
- Experimental 7-day prediction horizon
- Simulated live price updates
- WebSocket-based real-time communication
- Interactive historical/prediction charts
- Responsive Next.js dashboard
- Python/FastAPI backend

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js • React • Tailwind CSS |
| Visualization | Recharts • Lucide React |
| Backend | FastAPI • Uvicorn • Python |
| Realtime | WebSockets |
| Machine Learning | scikit-learn Random Forest |
| Data | Pandas • NumPy • yfinance |

## Project Structure

```text
.
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── package.json
└── README.md
```

## Local Development

### Prerequisites

- Python 3.x
- Node.js 18+
- npm

### 1. Start the backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
.\venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies and start FastAPI:

```bash
pip install -r requirements.txt
python main.py
```

Backend:
`http://localhost:8000`

### 2. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:
`http://localhost:3000`

## Machine-Learning Pipeline

```text
Historical Data
      ↓
Data Cleaning / Preparation
      ↓
Feature Construction
      ↓
Random Forest Training
      ↓
Prediction Generation
      ↓
API Response
      ↓
Interactive Visualization
```

The current implementation uses the recent historical dataset to train a Random Forest regression model and produces a short prediction horizon. Model quality can vary substantially with market regime, data quality, feature selection, and evaluation methodology.

## Engineering Considerations

For a production-grade forecasting system, the next engineering steps would include:

- Strict train/validation/test time splits
- Walk-forward backtesting
- Baseline models for comparison
- Prediction intervals and uncertainty estimates
- Feature importance and model diagnostics
- Data caching and rate-limit handling
- Structured API error handling
- Observability and model-performance monitoring
- Reproducible model/version tracking

## Security & Reliability

- Keep external API/data-provider credentials out of source control.
- Validate API inputs before processing ticker symbols or date ranges.
- Add rate limiting before exposing the API publicly.
- Restrict CORS to trusted frontend origins in production.
- Handle upstream data-provider failures gracefully.

## Project Value

This project demonstrates practical integration of **machine learning, financial-data pipelines, Python APIs, WebSockets, and modern React/Next.js visualization** in a single full-stack application.

## Author

**Pankaj (Tony) Kumar**  
AI Engineer • Full Stack Developer • Generative AI & RAG Specialist

[GitHub](https://github.com/hack2ai) • [LinkedIn](https://www.linkedin.com/in/pankaj-kumar-ab591a216)
