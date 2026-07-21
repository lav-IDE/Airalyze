import { Card } from "@/components/ui/card";
import { Activity, Clock3, TrendingUp } from "lucide-react";

export default function ForecastSignal({ forecast, error, isLoading }) {
  if (!forecast) {
    return (
      <Card className="bg-slate-900 border-slate-800 p-6 text-white">
        <h2 className="text-xl font-semibold">Live forecast signal</h2>
        <p className="mt-4 text-slate-300">
          {isLoading ? "Loading live signal…" : error || "Forecast temporarily unavailable"}
        </p>
      </Card>
    );
  }

  const { recommendation } = forecast;
  const generatedAt = forecast.data_timestamp
    ? new Date(forecast.data_timestamp).toLocaleString()
    : "Not available";

  return (
    <Card className="bg-slate-900 border-slate-800 p-6 text-white">
      <div className="flex items-center gap-3">
        <Activity className="text-cyan-400" />
        <h2 className="text-xl font-semibold">Live forecast signal</h2>
      </div>

      <div className="mt-6 rounded-lg bg-slate-800 p-4">
          <p className="text-xs text-slate-400">Expected AQI</p>
          <p className="mt-1 text-3xl font-bold text-cyan-400">{forecast.forecast_aqi}</p>
          <p className="text-sm text-slate-300">{forecast.aqi_band}</p>
          <p className="mt-2 text-sm capitalize text-slate-300">{recommendation?.trend ?? "Unknown"} trend</p>
      </div>

      <div className="mt-5 space-y-3 text-sm text-slate-300">
        <p className="flex gap-2"><Clock3 className="mt-0.5 size-4 text-cyan-400" />Updated {generatedAt}</p>
        <p className="flex gap-2"><TrendingUp className="mt-0.5 size-4 text-orange-400" />{recommendation?.suggested_actions?.[0] || "No operational action is currently suggested."}</p>
      </div>
    </Card>
  );
}
