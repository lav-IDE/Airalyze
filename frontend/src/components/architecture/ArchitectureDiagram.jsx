import { Card } from "@/components/ui/card";
import {
  Database,
  CloudSun,
  Cpu,
  BrainCircuit,
  BellRing,
  MonitorSmartphone,
  ArrowDown,
} from "lucide-react";

const steps = [
  {
    title: "CPCB station data",
    subtitle: "Recent AQI observations",
    icon: Database,
    color: "text-cyan-400",
  },
  {
    title: "Weather features",
    subtitle: "Local conditions",
    icon: CloudSun,
    color: "text-yellow-400",
  },
  {
    title: "Feature Engineering",
    subtitle: "Merge + Clean + Prepare",
    icon: Cpu,
    color: "text-purple-400",
  },
  {
    title: "Forecast Model",
    subtitle: "24-hour AQI prediction",
    icon: BrainCircuit,
    color: "text-red-400",
  },
  {
    title: "LLM Advisory",
    subtitle: "Citizen Recommendations",
    icon: BellRing,
    color: "text-green-400",
  },
  {
    title: "Dashboard",
    subtitle: "Citizen forecast dashboard",
    icon: MonitorSmartphone,
    color: "text-blue-400",
  },
];

export default function ArchitectureDiagram() {
  return (
    <Card className="bg-slate-900 border-slate-800 p-8 text-white">

      <h2 className="text-2xl font-semibold mb-3">
        System Architecture
      </h2>

      <p className="text-slate-400 mb-10">
        End-to-end pipeline from air quality data collection
        to multilingual citizen advisories.
      </p>

      <div className="flex flex-col items-center">

        {steps.map((step, index) => {
          const Icon = step.icon;

          return (
            <div
              key={step.title}
              className="flex flex-col items-center w-full"
            >

              <div className="w-full max-w-md rounded-xl bg-slate-800 border border-slate-700 p-6">

                <div className="flex items-center gap-5">

                  <div className="rounded-full bg-slate-900 p-4">
                    <Icon
                      className={step.color}
                      size={28}
                    />
                  </div>

                  <div>

                    <h3 className="text-lg font-semibold">
                      {step.title}
                    </h3>

                    <p className="text-slate-400">
                      {step.subtitle}
                    </p>

                  </div>

                </div>

              </div>

              {index !== steps.length - 1 && (
                <ArrowDown
                  className="my-4 text-slate-500"
                  size={28}
                />
              )}

            </div>
          );
        })}

      </div>

    </Card>
  );
}
