import { Card } from "@/components/ui/card";
import { MapPinned } from "lucide-react";

export default function WardSelector({
  wards,
  selectedWardId,
  setSelectedWard,
}) {
  return (
    <Card className="bg-slate-900 border-slate-800 p-6 text-white">

      <div className="flex items-center gap-3 mb-6">
        <MapPinned className="text-cyan-400" />
        <h2 className="text-xl font-semibold">
          Ward Forecast Dashboard
        </h2>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <select value={selectedWardId ?? ""} onChange={(event) => setSelectedWard(event.target.value || null)} className="rounded-xl border border-slate-700 bg-slate-800 px-5 py-3 text-white outline-none focus:border-cyan-400">
          <option value="">Select your ward</option>
          {wards.map((ward) => <option key={ward.id} value={ward.id}>{ward.name}</option>)}
        </select>
        {selectedWardId && <button onClick={() => setSelectedWard(null)} className="rounded-xl border border-slate-700 px-4 py-3 text-slate-200 hover:bg-slate-800">Change ward</button>}
      </div>

    </Card>
  );
}
