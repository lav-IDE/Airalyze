import { Shield } from "lucide-react";

export default function DashboardHeader() {
  return (
    <div className="flex justify-between items-center">

      <div>

        <h1 className="text-4xl font-bold">
          Municipal Command Center
        </h1>

        <p className="text-slate-400 mt-2">
          Review AI predictions and issue public health advisories.
        </p>

      </div>

      <div className="flex items-center gap-3 bg-slate-900 px-5 py-3 rounded-xl border border-slate-800">

        <Shield className="text-cyan-400"/>

        <div>

          <p className="font-semibold">
            Delhi Pollution Control Board
          </p>

          <p className="text-xs text-slate-400">
            Logged in
          </p>

        </div>

      </div>

    </div>
  );
}