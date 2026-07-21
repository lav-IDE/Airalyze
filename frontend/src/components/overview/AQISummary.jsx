import { Card } from "@/components/ui/card";
import {
  Wind,
  MapPin,
  AlertTriangle,
  TrendingUp,
} from "lucide-react";

export default function AQISummary({ forecast, selectedWard, error, isLoading }) {
  if (!forecast) {
    return (
      <div className="grid grid-cols-2 gap-4">
        <Card className="bg-slate-900 border-slate-800 p-5 text-white">
          {isLoading ? "Loading forecast…" : error || "Forecast temporarily unavailable"}
        </Card>
      </div>
    );
  }

  const trend =
    forecast.recommendation?.trend ?? "Unknown";

  const bandColor = {
    Good: "text-green-400",
    Satisfactory: "text-lime-400",
    Moderate: "text-yellow-400",
    Poor: "text-orange-400",
    "Very Poor": "text-red-400",
    Severe: "text-red-600",
  };

  const aqiColor =
    bandColor[forecast.aqi_band] || "text-cyan-400";

  return (
    <div className="grid grid-cols-2 gap-4 h-full">

      <Card className="bg-slate-900 border-slate-800 p-5">

        <div className="flex items-center justify-between">

          <div>
            <p className="text-slate-400 text-sm">
              Forecast AQI
            </p>

            <h2 className={`text-4xl font-bold mt-2 ${aqiColor}`}>
              {forecast.forecast_aqi}
            </h2>

            <p className="text-slate-400 mt-1">
              {forecast.aqi_band}
            </p>

          </div>

          <Wind className="text-cyan-400" size={32} />

        </div>

      </Card>

      <Card className="bg-slate-900 border-slate-800 p-5">

        <div className="flex items-center justify-between">

          <div>

            <p className="text-slate-400 text-sm">
              Forecast Time
            </p>

            <h2 className="text-xl font-bold text-white mt-2">
              {new Date(forecast.forecast_for).toLocaleString()}
            </h2>

          </div>

          <AlertTriangle
            className="text-yellow-400"
            size={32}
          />

        </div>

      </Card>

      <Card className="bg-slate-900 border-slate-800 p-5">

        <div className="flex items-center justify-between">

          <div>

            <p className="text-slate-400 text-sm">
              Selected Ward
            </p>

            <h2 className="text-2xl font-bold text-white mt-2">
              {selectedWard}
            </h2>

          </div>

          <MapPin
            className="text-red-400"
            size={32}
          />

        </div>

      </Card>

      <Card className="bg-slate-900 border-slate-800 p-5">

        <div className="flex items-center justify-between">

          <div>

            <p className="text-slate-400 text-sm">
              Trend
            </p>

            <h2 className="text-2xl font-bold text-orange-400 mt-2 capitalize">
              {trend}
            </h2>

          </div>

          <TrendingUp
            className="text-orange-400"
            size={32}
          />

        </div>

      </Card>

    </div>
  );
}
