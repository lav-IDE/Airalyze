import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { BriefcaseBusiness, HeartPulse, Hospital, School, ShieldAlert } from "lucide-react";

import { getAdvisory } from "@/services/api";

const icons = [School, Hospital, HeartPulse, BriefcaseBusiness];
const groups = ["Schools", "Hospitals", "Older residents", "Outdoor workers"];

export default function AdvisoryCard({ ward, forecast }) {
  const [profile, setProfile] = useState({ age_group: "adult", health_conditions: ["none"], activity: "indoor", language: "en" });
  const [advisory, setAdvisory] = useState(null);
  const [error, setError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const updateProfile = (name, value) => {
    setProfile((current) => {
      const updated = { ...current, [name]: name === "health_conditions" ? [value] : value };
      if (advisory && name === "language") {
        setIsGenerating(true);
        setError("");
        getAdvisory(ward.id, updated)
          .then((result) => setAdvisory(result))
          .catch((requestError) => setError(requestError.message || "Advisory temporarily unavailable"))
          .finally(() => setIsGenerating(false));
      }
      return updated;
    });
  };

  const generateAdvisory = () => {
    if (!forecast) return;
    setIsGenerating(true);
    setAdvisory(null);
    setError("");
    getAdvisory(ward.id, profile)
      .then((result) => setAdvisory(result))
      .catch((requestError) => setError(requestError.message || "Advisory temporarily unavailable"))
      .finally(() => setIsGenerating(false));
  };

  return (
    <Card className="bg-slate-900 border-slate-800 p-6 text-white">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <ShieldAlert className="text-red-400" />
          <h2 className="text-xl font-semibold">Citizen Health Advisory</h2>
        </div>
        <div className="flex flex-wrap justify-end gap-2 rounded-lg bg-slate-800 p-1 text-sm">
          {[
            { code: "en", label: "EN" },
            { code: "hi", label: "हिंदी" },
            { code: "pa", label: "ਪੰਜਾਬੀ" },
            { code: "ur", label: "اردو" },
          ].map((option) => (
            <button
              key={option.code}
              onClick={() => updateProfile("language", option.code)}
              className={`rounded-md px-3 py-1.5 whitespace-nowrap ${profile.language === option.code ? "bg-cyan-500 font-semibold text-black" : "text-slate-300"}`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
        <select aria-label="Age group" value={profile.age_group} onChange={(event) => updateProfile("age_group", event.target.value)} className="rounded-lg bg-slate-800 p-2 text-slate-200"><option value="child">Child</option><option value="adult">Adult</option><option value="elderly">Older adult</option></select>
        <select aria-label="Health consideration" value={profile.health_conditions[0]} onChange={(event) => updateProfile("health_conditions", event.target.value)} className="rounded-lg bg-slate-800 p-2 text-slate-200"><option value="none">No condition</option><option value="asthma">Asthma</option><option value="heart_disease">Heart condition</option><option value="pregnant">Pregnant</option></select>
        <select aria-label="Activity" value={profile.activity} onChange={(event) => updateProfile("activity", event.target.value)} className="rounded-lg bg-slate-800 p-2 text-slate-200"><option value="indoor">Mostly indoors</option><option value="commuter">Commuter</option><option value="outdoor_worker">Outdoor work</option><option value="exercise_planned">Exercise planned</option></select>
      </div>

      <button
        type="button"
        onClick={generateAdvisory}
        disabled={!forecast || isGenerating}
        className="mt-4 w-full rounded-xl bg-cyan-500 px-4 py-3 text-sm font-semibold text-black transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isGenerating ? "Generating advisory…" : "Generate advisory"}
      </button>

      <div className="mt-5 rounded-xl border border-slate-700 bg-slate-800 p-4">
        <p className="font-semibold">{advisory?.app.headline || ward.name}</p>
        <p className="mt-1 text-sm text-slate-300">{advisory?.app.advisory_text || error || "Generating advisory…"}</p>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-2 text-sm text-slate-300">
        {(advisory?.app.precautions || groups).map((item, index) => { const Icon = icons[index % icons.length]; return <div key={item} className="flex items-center gap-2 rounded-lg bg-slate-800 p-2"><Icon className="size-4 text-cyan-400" />{item}</div>; })}
      </div>
    </Card>
  );
}
