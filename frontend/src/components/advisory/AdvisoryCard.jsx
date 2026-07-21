import { Card } from "@/components/ui/card";
import { BriefcaseBusiness, HeartPulse, Hospital, School, ShieldAlert } from "lucide-react";

const copy = {
  English: {
    title: "Citizen Health Advisory",
    groups: ["Schools", "Hospitals", "Elderly residents", "Outdoor workers"],
    advisory: (ward, aqi, band) => `${ward}: the 1-hour AQI forecast is ${aqi} (${band}). Sensitive groups should limit prolonged outdoor exposure.`,
  },
  Hindi: {
    title: "नागरिक स्वास्थ्य सलाह",
    groups: ["स्कूल", "अस्पताल", "बुजुर्ग निवासी", "बाहरी कर्मचारी"],
    advisory: (ward, aqi, band) => `${ward}: 1 घंटे का AQI पूर्वानुमान ${aqi} (${band}) है। संवेदनशील समूह लंबे समय तक बाहर रहने से बचें।`,
  },
};

const icons = [School, Hospital, HeartPulse, BriefcaseBusiness];

export default function AdvisoryCard({ ward, forecast, language, setLanguage }) {
  const text = copy[language];

  return (
    <Card className="bg-slate-900 border-slate-800 p-6 text-white">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3"><ShieldAlert className="text-red-400" /><h2 className="text-xl font-semibold">{text.title}</h2></div>
        <div className="flex rounded-lg bg-slate-800 p-1 text-sm">
          {["English", "Hindi"].map((option) => <button key={option} onClick={() => setLanguage(option)} className={`rounded-md px-3 py-1.5 ${language === option ? "bg-cyan-500 font-semibold text-black" : "text-slate-300"}`}>{option === "Hindi" ? "हिंदी" : "EN"}</button>)}
        </div>
      </div>

      <div className="mt-5 rounded-xl border border-slate-700 bg-slate-800 p-4">
        <p className="font-semibold">{ward.name}</p>
        <p className="mt-1 text-sm text-slate-300">{forecast ? text.advisory(ward.name, forecast.forecast_aqi, forecast.aqi_band) : "Forecast temporarily unavailable."}</p>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-2 text-sm text-slate-300">
        {text.groups.map((group, index) => { const Icon = icons[index]; return <div key={group} className="flex items-center gap-2 rounded-lg bg-slate-800 p-2"><Icon className="size-4 text-cyan-400" />{group}</div>; })}
      </div>
    </Card>
  );
}
