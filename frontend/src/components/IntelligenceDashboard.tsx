"use client";

import { BarChart3, BrainCircuit, ShieldAlert, TrendingDown, TrendingUp } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Analysis } from "@/types/analysis";

const formatNumber = (value: number | null | undefined, digits = 2) =>
  typeof value === "number" && Number.isFinite(value) ? value.toFixed(digits) : "—";

export default function IntelligenceDashboard({ analysis }: { analysis: Analysis }) {
  const prediction = analysis.prediction;
  const positive = prediction.expected_change_percent >= 0;
  const topFeatures = Object.entries(prediction.feature_importance ?? {}).slice(0, 5);
  const chartData = (analysis.history ?? []).map((item) => ({ date: item.date.slice(5), close: item.close }));

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6 backdrop-blur-xl lg:col-span-2">
        <div className="mb-6 flex items-center gap-3"><BrainCircuit className="text-blue-400" /><div><h2 className="text-xl font-bold">AI Market Intelligence</h2><p className="text-sm text-slate-400">Next-session statistical estimate</p></div></div>
        <div className="grid gap-4 sm:grid-cols-3">
          <MetricCard label="Current Close" value={`$${formatNumber(analysis.latest_market.close)}`} />
          <MetricCard label="AI Estimate" value={`$${formatNumber(prediction.predicted_next_close)}`} />
          <MetricCard label="Expected Change" value={`${positive ? "+" : ""}${formatNumber(prediction.expected_change_percent)}%`} className={positive ? "text-emerald-400" : "text-red-400"} />
        </div>
      </section>

      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6 backdrop-blur-xl">
        <div className="flex items-center gap-3"><ShieldAlert className="text-amber-400" /><h2 className="font-bold">Signal</h2></div>
        <div className="mt-6 flex items-center gap-3">{positive ? <TrendingUp className="text-emerald-400" /> : <TrendingDown className="text-red-400" />}<span className="text-2xl font-black">{prediction.trend}</span></div>
        <p className="mt-4 text-sm text-slate-400">Model confidence score: <strong className="text-white">{formatNumber(prediction.confidence_score, 1)}%</strong></p>
      </section>

      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6 lg:col-span-2">
        <h3 className="mb-5 font-semibold">Historical Closing Price</h3>
        <div className="h-80 min-h-[320px] w-full min-w-0">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320} minWidth={1} minHeight={320}>
              <AreaChart data={chartData}>
                <defs><linearGradient id="closeGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3b82f6" stopOpacity={0.35} /><stop offset="100%" stopColor="#3b82f6" stopOpacity={0} /></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={["auto", "auto"]} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value: number | string | readonly (number | string)[] | undefined) => {
                  const rawValue = Array.isArray(value) ? value[0] : value;
                  return `$${formatNumber(typeof rawValue === "number" ? rawValue : Number(rawValue))}`;
                }} />
                <Area type="monotone" dataKey="close" stroke="#3b82f6" fill="url(#closeGradient)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : <div className="flex h-full items-center justify-center text-sm text-slate-500">Historical data is unavailable.</div>}
        </div>
      </section>

      <section className="rounded-2xl border border-blue-500/30 bg-blue-500/5 p-6">
        <h3 className="font-semibold">Market Snapshot</h3>
        <div className="mt-5 space-y-4">
          <div><p className="text-xs text-slate-500">Latest close</p><p className="text-xl font-bold">${formatNumber(analysis.latest_market.close)}</p></div>
          <div><p className="text-xs text-slate-500">AI estimate</p><p className="text-xl font-bold text-blue-400">${formatNumber(prediction.predicted_next_close)}</p></div>
          <div><p className="text-xs text-slate-500">Trading volume</p><p className="text-xl font-bold">{Number(analysis.latest_market.volume ?? 0).toLocaleString()}</p></div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6">
        <div className="mb-4 flex items-center gap-2"><BarChart3 size={18} /><h3 className="font-semibold">Technical Indicators</h3></div>
        <div className="grid grid-cols-2 gap-3 text-sm">{Object.entries(analysis.technical_indicators ?? {}).slice(0, 8).map(([key, value]) => <div key={key} className="rounded-lg bg-slate-900/60 p-3"><p className="text-slate-500">{key.replaceAll("_", " ")}</p><p className="font-bold">{formatNumber(value)}</p></div>)}</div>
      </section>

      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6">
        <h3 className="mb-4 font-semibold">Model Quality</h3>
        <div className="space-y-3 text-sm"><p>MAE <span className="float-right font-bold">{formatNumber(prediction.metrics?.mae, 4)}</span></p><p>RMSE <span className="float-right font-bold">{formatNumber(prediction.metrics?.rmse, 4)}</span></p><p>R² <span className="float-right font-bold">{formatNumber(prediction.metrics?.r2, 4)}</span></p></div>
      </section>

      <section className="rounded-2xl border border-slate-700/60 bg-slate-800/40 p-6">
        <h3 className="mb-4 font-semibold">Top Model Features</h3>
        {topFeatures.length > 0 ? <div className="space-y-3">{topFeatures.map(([name, score]) => <div key={name}><div className="mb-1 flex justify-between text-xs"><span>{name}</span><span>{formatNumber(score * 100, 1)}%</span></div><div className="h-2 rounded bg-slate-700"><div className="h-2 rounded bg-blue-500" style={{ width: `${Math.min(Math.max(score * 100 * 4, 0), 100)}%` }} /></div></div>)}</div> : <p className="text-sm text-slate-500">Feature importance is unavailable for this analysis.</p>}
      </section>
    </div>
  );
}

function MetricCard({ label, value, className = "" }: { label: string; value: string; className?: string }) {
  return <div className="rounded-xl bg-slate-900/60 p-4"><p className="text-sm text-slate-400">{label}</p><p className={`text-2xl font-bold ${className}`}>{value}</p></div>;
}
