"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import { Search, TrendingUp, Activity, ServerCrash } from "lucide-react";
import StockChart from "@/components/StockChart";
import MetricsPanel from "@/components/MetricsPanel";

export default function Home() {
  const [ticker, setTicker] = useState("AAPL");
  const [searchInput, setSearchInput] = useState("");
  const [data, setData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Real-time state
  const [livePrice, setLivePrice] = useState(null);
  const [liveChange, setLiveChange] = useState(0);
  const [liveChangePercent, setLiveChangePercent] = useState(0);
  
  const wsRef = useRef<WebSocket | null>(null);

  const fetchData = useCallback(async (symbol: string) => {
    setLoading(true);
    setError("");
    try {
      const histRes = await axios.get(`http://localhost:8000/api/historical/${symbol}`);
      if (histRes.data.error) throw new Error(histRes.data.error);
      
      const predRes = await axios.get(`http://localhost:8000/api/predict/${symbol}?days=7`);
      if (predRes.data.error) throw new Error(predRes.data.error);

      setData(histRes.data.data);
      setPredictions(predRes.data.predictions);
      setMetrics(predRes.data.metrics);
      setTicker(symbol);
      
      // Initialize WebSocket connection
      if (wsRef.current) {
        wsRef.current.close();
      }
      wsRef.current = new WebSocket(`ws://localhost:8000/ws/stock/${symbol}`);
      
      wsRef.current.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        setLivePrice(msg.price);
        setLiveChange(msg.change);
        setLiveChangePercent(msg.change_percent);
      };
      
    } catch (err: any) {
      setError(err.message || "Failed to fetch data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData("AAPL");
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [fetchData]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchInput.trim().toUpperCase();
    if (query) {
      // Map common names to Yahoo Finance symbols
      const tickerMap: Record<string, string> = {
        "NIFTY 50": "^NSEI",
        "NIFTY": "^NSEI",
        "S&P 500": "^GSPC",
        "DOW JONES": "^DJI",
        "DOW": "^DJI",
        "NASDAQ": "^IXIC",
        "BITCOIN": "BTC-USD",
        "BTC": "BTC-USD",
        "ETHEREUM": "ETH-USD",
        "ETH": "ETH-USD"
      };
      
      const symbol = tickerMap[query] || query;
      fetchData(symbol);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-100 p-6 md:p-12 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-500/20 text-blue-400 rounded-xl">
              <TrendingUp size={28} />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-white">AI Stock Predictor</h1>
              <p className="text-slate-400 text-sm">Real-time machine learning forecasts</p>
            </div>
          </div>

          <form onSubmit={handleSearch} className="relative w-full md:w-80">
            <input
              type="text"
              placeholder="Search ticker (e.g. TSLA, MSFT)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full bg-slate-800/50 border border-slate-700 focus:border-blue-500 rounded-full py-3 px-5 pl-12 outline-none transition-all placeholder:text-slate-500"
            />
            <Search className="absolute left-4 top-3.5 text-slate-400" size={18} />
          </form>
        </header>

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl flex items-center gap-3">
            <ServerCrash size={20} />
            {error}
          </div>
        )}

        {loading ? (
          <div className="h-[500px] flex flex-col justify-center items-center gap-4">
            <div className="w-10 h-10 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
            <p className="text-slate-400 animate-pulse">Running ML inference...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Main Chart Area */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* Ticker Header & Live Price */}
              <div className="p-6 bg-slate-800/40 border border-slate-700/50 rounded-2xl backdrop-blur-xl flex justify-between items-center">
                <div>
                  <h2 className="text-4xl font-black text-white">{ticker}</h2>
                  <p className="text-slate-400 flex items-center gap-2">
                    <Activity size={14} className="text-emerald-400 animate-pulse"/> 
                    Live Connection Active
                  </p>
                </div>
                
                <div className="text-right">
                  <p className="text-3xl font-bold text-white">
                    ${livePrice ? livePrice.toFixed(2) : ((data[data.length-1] as any)?.Close || 0).toFixed(2)}
                  </p>
                  <p className={`text-lg font-medium flex justify-end gap-2 ${liveChange >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    <span>{liveChange >= 0 ? '+' : ''}{liveChange ? liveChange.toFixed(2) : '0.00'}</span>
                    <span>({liveChange >= 0 ? '+' : ''}{liveChangePercent ? liveChangePercent.toFixed(2) : '0.00'}%)</span>
                  </p>
                </div>
              </div>

              {/* Chart Component */}
              <div className="p-6 bg-slate-800/40 border border-slate-700/50 rounded-2xl backdrop-blur-xl h-[500px]">
                <StockChart data={data} predictions={predictions} />
              </div>
            </div>

            {/* Metrics Sidebar */}
            <div className="space-y-6">
              <MetricsPanel metrics={metrics} />
              
              <div className="p-6 bg-blue-500/10 border border-blue-500/20 rounded-2xl">
                <h3 className="text-lg font-semibold text-blue-300 mb-2">Model Information</h3>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Predictions are generated on the fly using a <strong>Random Forest Regressor</strong> trained on the past 2 years of daily closing prices. 
                  Real-time price streams simulate intra-day market volatility over the base REST data.
                </p>
              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
