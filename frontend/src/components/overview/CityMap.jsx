import { Card } from "@/components/ui/card";

function Sparkline({ points, prediction }) {
  const actualValues = points?.map((point) => point.aqi).filter(Number.isFinite) ?? [];
  const values = [...actualValues, prediction].filter(Number.isFinite);
  if (actualValues.length < 2 || !Number.isFinite(prediction)) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const spread = max - min || 1;
  const pointFor = (value, index, total) => {
    const x = (index / (total - 1)) * 100;
    const y = 28 - ((value - min) / spread) * 24;
    return `${x},${y}`;
  };
  const actualCoordinates = actualValues.map((value, index) => pointFor(value, index, values.length)).join(" ");
  const lastActual = pointFor(actualValues.at(-1), actualValues.length - 1, values.length);
  const predictedX = 100;
  const predictedY = 28 - ((prediction - min) / spread) * 24;

  return (
    <div className="mt-5">
      <div className="mb-1 flex justify-between text-xs text-white/70">
        <span>Last {values.length - 1} hours actual</span><span>+1h forecast</span>
      </div>
      <svg viewBox="0 0 100 32" preserveAspectRatio="none" className="h-12 w-full overflow-visible" aria-label="Recent actual AQI and one-hour forecast">
        <polyline points={actualCoordinates} fill="none" stroke="#ffffff" strokeWidth="2" vectorEffect="non-scaling-stroke" />
        <line x1={lastActual.split(",")[0]} y1={lastActual.split(",")[1]} x2={predictedX} y2={predictedY} stroke="#22d3ee" strokeWidth="2" strokeDasharray="4 3" vectorEffect="non-scaling-stroke" />
        {actualValues.map((value, index) => { const [x, y] = pointFor(value, index, values.length).split(","); return <circle key={index} cx={x} cy={y} r="2" fill="#ffffff" vectorEffect="non-scaling-stroke" />; })}
        <circle cx={predictedX} cy={predictedY} r="3" fill="#22d3ee" vectorEffect="non-scaling-stroke" />
      </svg>
    </div>
  );
}

export default function CityMap({ ward, forecast, error, isLoading }) {

  const getColor = (status) => {
    switch (status) {
      case "Good":
        return "bg-green-600";
      case "Satisfactory":
        return "bg-lime-600";
      case "Moderate":
        return "bg-yellow-500";
      case "Poor":
        return "bg-orange-500";
      case "Very Poor":
        return "bg-red-500";
      case "Severe":
        return "bg-red-700";
      default:
        return "bg-slate-700";
    }
  };

  return (
    <Card className="bg-slate-900 border-slate-800 p-6">

      <div className="mb-6">
        <h2 className="text-xl font-semibold text-white">
          Delhi Ward AQI Overview
        </h2>

        <p className="text-slate-400 text-sm mt-1">
          Live forecast from the backend
        </p>
      </div>

      <div>
          <div className={`${getColor(forecast?.aqi_band)} rounded-xl p-6`}>
            <h3 className="text-xl font-bold text-white">
              {ward.name}
            </h3>

            <p className="mt-4 text-white/80">
              Forecast AQI
            </p>

            <h1 className="text-5xl font-bold text-white mt-1">
              {forecast?.forecast_aqi ?? (isLoading ? "Loading…" : "--")}
            </h1>

            <p className="mt-5 bg-white/20 rounded-lg inline-block px-3 py-1 text-white">
              {forecast?.aqi_band ?? (error ? "Temporarily unavailable" : "Loading…")}
            </p>

            {forecast && <Sparkline points={forecast.recent_actuals} prediction={forecast.forecast_aqi} />}
            {forecast?.accuracy_metrics && <div className="mt-5 grid grid-cols-3 gap-2 border-t border-white/20 pt-4 text-center text-white"><div><p className="text-xs text-white/70">Model RMSE</p><p className="font-semibold">{forecast.accuracy_metrics.model_rmse}</p></div><div><p className="text-xs text-white/70">Baseline RMSE</p><p className="font-semibold">{forecast.accuracy_metrics.baseline_rmse}</p></div><div><p className="text-xs text-white/70">Improvement</p><p className="font-semibold">{forecast.accuracy_metrics.improvement_percent}%</p></div></div>}
            {forecast?.accuracy_metrics && <p className="mt-3 text-xs text-white/65">Trained on {forecast.accuracy_metrics.training_window_days} days of CPCB station data.</p>}
          </div>
      </div>

    </Card>
  );
}
