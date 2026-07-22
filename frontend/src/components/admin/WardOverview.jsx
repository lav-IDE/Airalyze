import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { getWards, getForecast } from "@/services/api";

const bandColor = {
  Good: "bg-green-500",
  Satisfactory: "bg-lime-500",
  Moderate: "bg-yellow-500",
  Poor: "bg-orange-500",
  "Very Poor": "bg-red-500",
  Severe: "bg-red-700",
};

export default function WardOverview() {
  const [wardData, setWardData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    getWards()
      .then(async (loadedWards) => {
        try {
          const promises = loadedWards.map(async (ward) => {
            const forecast = await getForecast(ward.id);
            return {
              id: ward.id,
              name: ward.name,
              aqi: Math.round(forecast.forecast_aqi),
              status: forecast.aqi_band,
              color: bandColor[forecast.aqi_band] || "bg-slate-500",
            };
          });
          const results = await Promise.all(promises);
          if (!cancelled) {
            setWardData(results);
            setIsLoading(false);
          }
        } catch (_err) {
          if (!cancelled) {
            setError("Failed to load forecast data.");
            setIsLoading(false);
          }
        }
      })
      .catch((_err) => {
        if (!cancelled) {
          setError("Failed to load wards.");
          setIsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <Card className="bg-slate-900 border-slate-800 p-6">
      <h2 className="text-xl font-semibold mb-6 text-white">
        Critical Wards
      </h2>

      {isLoading ? (
        <div className="text-slate-400 text-sm">Loading ward details…</div>
      ) : error ? (
        <div className="text-red-400 text-sm">{error}</div>
      ) : (
        <div className="space-y-4">
          {wardData.map((ward) => (
            <div
              key={ward.id}
              className="rounded-xl bg-slate-800 p-4"
            >
              <div className="flex justify-between items-center">
                <h3 className="text-white font-medium">{ward.name}</h3>
                <span
                  className={`w-3 h-3 rounded-full ${ward.color}`}
                />
              </div>

              <p className="mt-3 text-3xl font-bold text-white">
                {ward.aqi}
              </p>

              <p className="text-slate-400 text-sm mt-1">
                {ward.status}
              </p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}