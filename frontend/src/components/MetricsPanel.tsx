import { Target, Activity, Zap, BarChart2 } from "lucide-react";

export default function MetricsPanel({ metrics }: { metrics: any }) {
  if (!metrics) return null;

  const cards = [
    { label: "Mean Absolute Error", value: metrics.MAE, icon: Target, color: "text-amber-400" },
    { label: "Root Mean Sq. Error", value: metrics.RMSE, icon: Zap, color: "text-orange-400" },
    { label: "R² Score", value: metrics.R2, icon: Activity, color: "text-emerald-400" },
    { label: "Mean Squared Error", value: metrics.MSE, icon: BarChart2, color: "text-blue-400" },
  ];

  return (
    <div className="grid grid-cols-2 gap-4">
      {cards.map((c, i) => (
        <div key={i} className="p-5 bg-slate-800/40 border border-slate-700/50 rounded-2xl flex flex-col items-center text-center justify-center gap-2 hover:bg-slate-700/50 transition-colors">
          <c.icon size={24} className={c.color} />
          <h4 className="text-slate-400 text-xs font-medium uppercase tracking-wider">{c.label}</h4>
          <p className="text-2xl font-bold text-white">{c.value}</p>
        </div>
      ))}
    </div>
  );
}
