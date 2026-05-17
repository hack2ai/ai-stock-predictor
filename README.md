# 📈 Real-Time AI Stock Predictor

This is a full-stack real-time stock price prediction application built with Next.js, Tailwind CSS, FastAPI, and Scikit-learn.

## 🚀 Features
- **Live Real-time Prices:** Simulates live stock prices updating every second.
- **AI Predictions:** Uses a Random Forest Regressor trained on the last 2 years of Yahoo Finance data to predict the next 7 days of price movement.
- **Dynamic Charting:** Interactive historical and predicted price chart using Recharts.

---

## 🛠️ How to Run Locally

To run this project on your machine, you need to start **both** the backend and the frontend servers. 

### 1. Start the Backend (FastAPI / Python)

Open a terminal in the root folder of this project and run the following commands:

```bash
# Move into the backend directory
cd backend

# Create a virtual environment (if you haven't already)
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install the Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```
The backend will start running at `http://localhost:8000`.

### 2. Start the Frontend (Next.js / React)

Open a **new** separate terminal in the root folder of this project and run:

```bash
# Move into the frontend directory
cd frontend

# Install the Node.js dependencies
npm install

# Start the Next.js development server
npm run dev
```

### 3. Open the App
Once both servers are running, open your web browser and go to:
**[http://localhost:3000](http://localhost:3000)**

---

## 📚 Tech Stack
- **Frontend:** Next.js, React, Tailwind CSS, Recharts, Lucide React
- **Backend:** FastAPI, Python, Uvicorn, WebSockets
- **Machine Learning:** Scikit-learn, Pandas, Numpy, yfinance
