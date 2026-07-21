import { Card } from "@/components/ui/card";

export default function MetricsCard({ selectedWard, forecast, error, isLoading }) {
  if (!forecast) {
    return (
      <Card className="bg-slate-900 border-slate-800 p-6 h-full">
        <p className="text-white">{isLoading ? "Loading forecast…" : error || "Forecast temporarily unavailable"}</p>
      </Card>
    );
  }

  const metrics = [
    {
      title: "Forecast AQI",
      value: forecast.forecast_aqi,
      subtitle: forecast.aqi_band,
    },
    {
      title: "Forecast Horizon",
      value: `${forecast.horizon_hours} hr`,
      subtitle: "Prediction window",
    },
    {
      title: "Model",
      value: forecast.model,
      subtitle: "Forecast model",
    },
  ];

  return (
    <Card className="bg-slate-900 border-slate-800 p-6 h-full">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-white">
          Forecast Details
        </h2>

        <p className="text-slate-400 text-sm mt-1">
          Live prediction for {selectedWard}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {metrics.map((metric) => (
          <Card
            key={metric.title}
            className="bg-slate-800 border-slate-700 p-4"
          >
            <p className="text-sm text-slate-400">
              {metric.title}
            </p>

            <h3 className="text-2xl font-bold text-cyan-400 mt-2">
              {metric.value}
            </h3>

            <p className="text-xs text-slate-500 mt-2">
              {metric.subtitle}
            </p>
          </Card>
        ))}
      </div>

      <div className="mt-6 border-t border-slate-800 pt-4">
        <p className="text-sm text-slate-400">
          Forecast generated using the{" "}
          <span className="text-cyan-400 font-semibold">
            {forecast.model}
          </span>{" "}
          model for{" "}
          <span className="text-white font-semibold">
            {selectedWard}
          </span>.
        </p>
      </div>
    </Card>
  );
}
