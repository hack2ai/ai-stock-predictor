"use client";

import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Area,
} from "recharts";

type MarketPoint = { Date: string; Close: number };
type PredictionPoint = { Date: string; Predicted_Price: number };

export default function StockChart({ data, predictions }: { data: MarketPoint[]; predictions: PredictionPoint[] }) {
  const formattedData = data.map((d) => ({ date: d.Date, historical: d.Close, predicted: null as number | null }));
  const formattedPreds = predictions.map((p) => ({ date: p.Date, historical: null as number | null, predicted: p.Predicted_Price }));

  if (formattedData.length > 0 && formattedPreds.length > 0) {
    formattedPreds[0].historical = formattedData[formattedData.length - 1].historical;
  }

  const chartData = [...formattedData, ...formattedPreds];

  if (chartData.length === 0) {
    return <div className="flex h-[320px] items-center justify-center text-sm text-slate-500">Chart data is unavailable.</div>;
  }

  return (
    <div className="h-[320px] w-full min-w-0">
      <ResponsiveContainer width="100%" height={320} minWidth={1} minHeight={320}>
        <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorHist" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorPred" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis dataKey="date" stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 12 }} tickFormatter={(val) => String(val).substring(5)} minTickGap={30} />
          <YAxis stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 12 }} domain={["auto", "auto"]} tickFormatter={(val) => `$${val}`} />
          <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#475569", color: "#f8fafc", borderRadius: "8px" }} itemStyle={{ color: "#e2e8f0" }} />
          <Legend wrapperStyle={{ paddingTop: "20px" }} />
          <Area type="monotone" dataKey="historical" name="Historical Price" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorHist)" />
          <Line type="monotone" dataKey="predicted" name="AI Prediction (7 Days)" stroke="#8b5cf6" strokeWidth={2} strokeDasharray="5 5" dot={{ r: 4, fill: "#8b5cf6", strokeWidth: 0 }} activeDot={{ r: 6 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
