import { Card } from "@/components/ui/card";
import { BrainCircuit } from "lucide-react";

const colors = ["bg-red-500", "bg-orange-500", "bg-blue-500", "bg-green-500", "bg-cyan-500"];

export default function FeatureImportance({ selectedWard, forecast, error, isLoading }) {
  const features = forecast?.prediction_drivers ?? [];
  return (
    <Card className="bg-slate-900 border-slate-800 p-6 text-white">

      <div className="flex items-center gap-3 mb-2">
        <BrainCircuit className="text-purple-400" />
        <h2 className="text-xl font-semibold">
          Prediction Drivers
        </h2>
      </div>

      <p className="text-slate-400 mb-6">
        Model driver weights for {selectedWard}
      </p>

      {isLoading && <p className="text-slate-300">Loading model drivers…</p>}
      {!isLoading && error && <p className="text-amber-300">Drivers are temporarily unavailable.</p>}
      {!isLoading && !error && features.length === 0 && (
        <p className="text-slate-300">This model does not expose feature-importance data.</p>
      )}

      <div className="space-y-5">

        {features.map((feature) => (

          <div key={feature.name}>

            <div className="flex justify-between mb-2">

              <span>{feature.name}</span>

              <span>{feature.weight}%</span>

            </div>

            <div className="h-3 rounded-full bg-slate-800 overflow-hidden">

              <div
                className={`${colors[features.indexOf(feature) % colors.length]} h-full rounded-full transition-all duration-700`}
                style={{
                  width: `${feature.weight}%`,
                }}
              />

            </div>

          </div>

        ))}

      </div>

      <div className="mt-8 rounded-xl border border-slate-700 bg-slate-800 p-4">

        <p className="text-sm text-slate-300">
          These percentages are grouped global feature-importance weights from
          the active model. They show what the model generally relies on, not
          a causal explanation or an individual prediction attribution.
        </p>

      </div>

    </Card>
  );
}
