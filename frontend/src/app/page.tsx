"use client";

import { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { BrainCircuit, Loader2, Search, ServerCrash, Sparkles } from "lucide-react";
import IntelligenceDashboard from "@/components/IntelligenceDashboard";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type Analysis = {
  ticker: string;
  latest_market: { close: number; volume: number };
  technical_indicators: Record<string, number | null>;
  prediction: {
    predicted_next_close: number;
    expected_change_percent: number;
    trend: string;
    confidence_score: number;
    metrics: { mae: number; rmse: number; r2: number };
    feature_importance: Record<string, number>;
    disclaimer: string;
  };
};

export default function Home() {
  const [ticker, setTicker] = useState("AAPL");
  const [query, setQuery] = useState("AAPL");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadAnalysis = useCallback(async (symbol: string) => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${API_BASE}/api/v1/stocks/${encodeURIComponent(symbol)}/analysis`);
      setAnalysis(response.data);
      setTicker(symbol);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) setError(err.response?.data?.detail || err.message);
      else setError("Unable to load market intelligence.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAnalysis("AAPL"); }, [loadAnalysis]);

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    const symbol = query.trim().toUpperCase();
    if (symbol) loadAnalysis(symbol);
  };

  return (
    <main className="min-h-screen bg-[#0b1120] text-slate-100 p-5 md:p-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div className="flex items-center gap-4">
            <div className="rounded-2xl bg-blue-500/15 p-4 text-blue-400"><BrainCircuit size={30} /></div>
            <div><h1 className="text-3xl font-black tracking-tight">AI Stock Intelligence</h1><p className="text-slate-400">Machine learning, technical analysis and transparent model metrics</p></div>
          </div>
          <form onSubmit={handleSearch} className="relative w-full md:w-96">
            <Search size={18} className="absolute left-4 top-3.5 text-slate-400" />
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="AAPL, TSLA, BTC-USD..." className="w-full rounded-xl border border-slate-700 bg-slate-800/70 py-3 pl-11 pr-24 outline-none focus:border-blue-500" />
            <button className="absolute right-1.5 top-1.5 rounded-lg bg-blue-600 px-4 py-1.5 text-sm font-semibold">Analyze</button>
          </form>
        </header>

        <div className="rounded-2xl border border-blue-500/20 bg-gradient-to-r from-blue-500/10 to-transparent p-6">
          <div className="flex items-start gap-3"><Sparkles className="mt-1 text-blue-400" /><div><h2 className="font-bold">{ticker} Market Analysis</h2><p className="mt-1 text-sm text-slate-400">Historical market data is processed into technical indicators and an ML prediction estimate.</p></div></div>
        </div>

        {error && <div className="flex gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300"><ServerCrash />{error}</div>}
        {loading && <div className="flex min-h-[420px] flex-col items-center justify-center gap-4 text-slate-400"><Loader2 className="animate-spin text-blue-400" size={36} /><p>Fetching market data and running AI analysis...</p></div>}
        {!loading && analysis && <IntelligenceDashboard analysis={analysis} />}

        {analysis && <footer className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 text-xs leading-relaxed text-slate-500">{analysis.prediction.disclaimer}</footer>}
      </div>
    </main>
  );
}
