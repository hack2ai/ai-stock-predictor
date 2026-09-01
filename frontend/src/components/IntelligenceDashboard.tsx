"use client";

import { BarChart3, BrainCircuit, ShieldAlert, TrendingDown, TrendingUp } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Analysis = {
  ticker: string;
  latest_market: { close: number; volume: number };
  history: { date: string; open: number; high: number; low: number; close: number; volume: number }[];
  technical_indicators: Record<string, number | null>;
  prediction: {
    predicted_next_close: number;
    prediction_interval: { lower: number; upper: number; confidence_level: number };
    expected_change_percent: number;
    trend: string;
    confidence_score: number;
    metrics: { mae: number; rmse: number; r2: number };
    validation: { method: string; samples: number };
    model: { algorithm: string; random_state: number };
    feature_importance: Record<string, number>;
  };
};

export default function IntelligenceDashboard({ analysis }: { analysis: Analysis }) {
  const prediction = analysis.prediction;
  const positive = prediction.expected_change_percent >= 0;
  const topFeatures = Object.entries(prediction.feature_importance).slice(0, 5);
  const chartData = analysis.history.map((item) => ({ date: item.date.slice(5), close: item.close }));

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <section className="lg:col-span-2 rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6 backdrop-blur-xl">
        <div className="mb-6 flex items-center gap-3"><BrainCircuit className="text-blue-400" /><div><h2 className="text-xl font-bold">AI Market Intelligence</h2><p className="text-sm text-slate-400">Next-session statistical estimate</p></div></div>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl bg-slate-900/60 p-4"><p className="text-sm text-slate-400">Current Close</p><p className="text-2xl font-bold">${analysis.latest_market.close.toFixed(2)}</p></div>
          <div className="rounded-xl bg-slate-900/60 p-4"><p className="text-sm text-slate-400">AI Estimate</p><p className="text-2xl font-bold">${prediction.predicted_next_close.toFixed(2)}</p></div>
          <div className="rounded-xl bg-slate-900/60 p-4"><p className="text-sm text-slate-400">Expected Change</p><p className={`text-2xl font-bold ${positive ? "text-emerald-400" : "text-red-400"}`}>{positive ? "+" : ""}{prediction.expected_change_percent.toFixed(2)}%</p></div>
        </div>
      </section>
      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6 backdrop-blur-xl"><div className="flex items-center gap-3"><ShieldAlert className="text-amber-400" /><h2 className="font-bold">Signal</h2></div><div className="mt-6 flex items-center gap-3">{positive ? <TrendingUp className="text-emerald-400" /> : <TrendingDown className="text-red-400" />}<span className="text-2xl font-black">{prediction.trend}</span></div><p className="mt-4 text-sm text-slate-400">Model confidence score: <strong className="text-white">{prediction.confidence_score.toFixed(1)}%</strong></p></section>

      <section className="lg:col-span-2 rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6"><h3 className="mb-5 font-semibold">Historical Closing Price</h3><div className="h-80"><ResponsiveContainer width="100%" height="100%"><AreaChart data={chartData}><defs><linearGradient id="closeGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3b82f6" stopOpacity={0.35}/><stop offset="100%" stopColor="#3b82f6" stopOpacity={0}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" stroke="#334155"/><XAxis dataKey="date" tick={{fontSize:12}}/><YAxis domain={["auto", "auto"]} tick={{fontSize:12}}/><Tooltip formatter={(value) => `$${Number(value ?? 0).toFixed(2)}`}/><Area type="monotone" dataKey="close" stroke="#3b82f6" fill="url(#closeGradient)" strokeWidth={2}/></AreaChart></ResponsiveContainer></div></section>

      <section className="rounded-2xl border border-blue-500/30 bg-blue-500/5 p-6"><h3 className="font-semibold">Prediction Uncertainty</h3><p className="mt-2 text-sm text-slate-400">{prediction.prediction_interval.confidence_level}% statistical interval</p><div className="mt-5 space-y-3"><div><p className="text-xs text-slate-500">Lower estimate</p><p className="text-xl font-bold">${prediction.prediction_interval.lower.toFixed(2)}</p></div><div><p className="text-xs text-slate-500">AI estimate</p><p className="text-xl font-bold text-blue-400">${prediction.predicted_next_close.toFixed(2)}</p></div><div><p className="text-xs text-slate-500">Upper estimate</p><p className="text-xl font-bold">${prediction.prediction_interval.upper.toFixed(2)}</p></div></div></section>

      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6"><div className="mb-4 flex items-center gap-2"><BarChart3 size={18}/><h3 className="font-semibold">Technical Indicators</h3></div><div className="grid grid-cols-2 gap-3 text-sm">{Object.entries(analysis.technical_indicators).slice(0, 8).map(([key, value]) => <div key={key} className="rounded-lg bg-slate-900/60 p-3"><p className="text-slate-500">{key.replaceAll("_", " ")}</p><p className="font-bold">{value === null ? "—" : value.toFixed(2)}</p></div>)}</div></section>
      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6"><h3 className="mb-4 font-semibold">Model Quality</h3><div className="space-y-3 text-sm"><p>MAE <span className="float-right font-bold">{prediction.metrics.mae}</span></p><p>RMSE <span className="float-right font-bold">{prediction.metrics.rmse}</span></p><p>R² <span className="float-right font-bold">{prediction.metrics.r2}</span></p></div></section>
      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6"><h3 className="mb-4 font-semibold">Validation</h3><p className="text-sm text-slate-400">Method</p><p className="font-semibold capitalize">{prediction.validation.method.replaceAll("_", " ")}</p><p className="mt-3 text-sm text-slate-400">Validation samples</p><p className="font-semibold">{prediction.validation.samples}</p><p className="mt-3 text-sm text-slate-400">Model</p><p className="text-sm font-semibold">{prediction.model.algorithm}</p></section>
      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6"><h3 className="mb-4 font-semibold">Top Model Features</h3><div className="space-y-3">{topFeatures.map(([name, score]) => <div key={name}><div className="mb-1 flex justify-between text-xs"><span>{name}</span><span>{(score * 100).toFixed(1)}%</span></div><div className="h-2 rounded bg-slate-700"><div className="h-2 rounded bg-blue-500" style={{ width: `${Math.min(score * 100 * 4, 100)}%` }} /></div></div>)}</div></section>
    </div>
  );
}
