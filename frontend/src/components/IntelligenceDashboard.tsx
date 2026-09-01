"use client";

import { BarChart3, BrainCircuit, ShieldAlert, TrendingDown, TrendingUp } from "lucide-react";

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
  };
};

export default function IntelligenceDashboard({ analysis }: { analysis: Analysis }) {
  const prediction = analysis.prediction;
  const positive = prediction.expected_change_percent >= 0;
  const topFeatures = Object.entries(prediction.feature_importance).slice(0, 5);

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <section className="lg:col-span-2 rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6 backdrop-blur-xl">
        <div className="flex items-center gap-3 mb-6">
          <BrainCircuit className="text-blue-400" />
          <div><h2 className="text-xl font-bold">AI Market Intelligence</h2><p className="text-sm text-slate-400">Next-session statistical estimate</p></div>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl bg-slate-900/60 p-4"><p className="text-sm text-slate-400">Current Close</p><p className="text-2xl font-bold">${analysis.latest_market.close.toFixed(2)}</p></div>
          <div className="rounded-xl bg-slate-900/60 p-4"><p className="text-sm text-slate-400">AI Estimate</p><p className="text-2xl font-bold">${prediction.predicted_next_close.toFixed(2)}</p></div>
          <div className="rounded-xl bg-slate-900/60 p-4"><p className="text-sm text-slate-400">Expected Change</p><p className={`text-2xl font-bold ${positive ? "text-emerald-400" : "text-red-400"}`}>{positive ? "+" : ""}{prediction.expected_change_percent.toFixed(2)}%</p></div>
        </div>
      </section>
      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6 backdrop-blur-xl">
        <div className="flex items-center gap-3"><ShieldAlert className="text-amber-400" /><h2 className="font-bold">Signal</h2></div>
        <div className="mt-6 flex items-center gap-3">{positive ? <TrendingUp className="text-emerald-400" /> : <TrendingDown className="text-red-400" />}<span className="text-2xl font-black">{prediction.trend}</span></div>
        <p className="mt-4 text-sm text-slate-400">Model confidence score: <strong className="text-white">{prediction.confidence_score.toFixed(1)}%</strong></p>
      </section>
      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6"><div className="flex items-center gap-2 mb-4"><BarChart3 size={18}/><h3 className="font-semibold">Technical Indicators</h3></div><div className="grid grid-cols-2 gap-3 text-sm">{Object.entries(analysis.technical_indicators).slice(0, 8).map(([key, value]) => <div key={key} className="rounded-lg bg-slate-900/60 p-3"><p className="text-slate-500">{key.replaceAll("_", " ")}</p><p className="font-bold">{value === null ? "—" : value.toFixed(2)}</p></div>)}</div></section>
      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6"><h3 className="font-semibold mb-4">Model Quality</h3><div className="space-y-3 text-sm"><p>MAE <span className="float-right font-bold">{prediction.metrics.mae}</span></p><p>RMSE <span className="float-right font-bold">{prediction.metrics.rmse}</span></p><p>R² <span className="float-right font-bold">{prediction.metrics.r2}</span></p></div></section>
      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6"><h3 className="font-semibold mb-4">Top Model Features</h3><div className="space-y-3">{topFeatures.map(([name, score]) => <div key={name}><div className="flex justify-between text-xs mb-1"><span>{name}</span><span>{(score * 100).toFixed(1)}%</span></div><div className="h-2 rounded bg-slate-700"><div className="h-2 rounded bg-blue-500" style={{ width: `${Math.min(score * 100 * 4, 100)}%` }} /></div></div>)}</div></section>
    </div>
  );
}
