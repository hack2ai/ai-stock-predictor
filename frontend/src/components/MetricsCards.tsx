"use client";

import { Activity, TrendingUp, TrendingDown, Target, Brain } from "lucide-react";

interface MetricsCardsProps {
  currentPrice: number;
  prediction: number;
  mae: number;
  rmse: number;
  isModelTrained: boolean;
}

export default function MetricsCards({
  currentPrice,
  prediction,
  mae,
  rmse,
  isModelTrained,
}: MetricsCardsProps) {
  const diff = prediction - currentPrice;
  const isUp = diff >= 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {/* Current Price Card */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-lg flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium mb-1">Current Price</p>
          <h2 className="text-3xl font-bold text-white">${currentPrice.toFixed(2)}</h2>
        </div>
        <div className="bg-blue-900/30 p-3 rounded-lg text-blue-400">
          <Activity size={24} />
        </div>
      </div>

      {/* Prediction Card */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-lg flex items-center justify-between relative overflow-hidden">
        <div className="z-10">
          <p className="text-gray-400 text-sm font-medium mb-1">AI Next Prediction</p>
          <div className="flex items-end gap-2">
            <h2 className="text-3xl font-bold text-white">
              {isModelTrained ? `$${prediction.toFixed(2)}` : "---"}
            </h2>
            {isModelTrained && (
              <span className={`text-sm font-medium mb-1 flex items-center ${isUp ? 'text-green-400' : 'text-red-400'}`}>
                {isUp ? <TrendingUp size={16} className="mr-1" /> : <TrendingDown size={16} className="mr-1" />}
                {Math.abs(diff).toFixed(2)}
              </span>
            )}
          </div>
        </div>
        <div className={`z-10 p-3 rounded-lg ${isUp ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
          <Brain size={24} />
        </div>
        {/* Subtle gradient background for visual flair */}
        <div className="absolute -right-6 -top-6 w-24 h-24 bg-purple-600/10 rounded-full blur-2xl"></div>
      </div>

      {/* Model Accuracy (MAE) */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-lg flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium mb-1">Mean Abs. Error (MAE)</p>
          <h2 className="text-2xl font-bold text-white">
            {isModelTrained ? mae.toFixed(4) : "---"}
          </h2>
        </div>
        <div className="bg-orange-900/30 p-3 rounded-lg text-orange-400">
          <Target size={24} />
        </div>
      </div>

      {/* Model Accuracy (RMSE) */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-lg flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium mb-1">Root Mean Sq. Error</p>
          <h2 className="text-2xl font-bold text-white">
            {isModelTrained ? rmse.toFixed(4) : "---"}
          </h2>
        </div>
        <div className="bg-purple-900/30 p-3 rounded-lg text-purple-400">
          <Target size={24} />
        </div>
      </div>
    </div>
  );
}
