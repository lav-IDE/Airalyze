import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Send } from "lucide-react";
import { getAdvisory } from "@/services/api";

export default function AdvisoryGenerator() {
  const [ward, setWard] = useState("anand_vihar");
  const [language, setLanguage] = useState("en");
  const [text, setText] = useState("");
  const [advisory, setAdvisory] = useState(null);
  const [error, setError] = useState("");

  function changeLanguage(lang) {
    setLanguage(lang);
  }

  useEffect(() => {
    let cancelled = false;
    setError("");
    getAdvisory(ward, {
      age_group: "adult",
      health_conditions: ["none"],
      activity: "indoor",
      language,
    })
      .then((result) => {
        if (cancelled) return;
        setAdvisory(result);
        setText(result.app.advisory_text);
      })
      .catch((requestError) => {
        if (cancelled) return;
        setAdvisory(null);
        setError(requestError.message || "Advisory temporarily unavailable");
      });

    return () => {
      cancelled = true;
    };
  }, [ward, language]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-slate-900 border-slate-800 p-6">
        <h2 className="text-2xl font-semibold text-white">
          Advisory Generation
        </h2>

        <p className="text-slate-300 mt-2">
          Generate multilingual advisories based on the predicted AQI.
        </p>
      </Card>

      {/* Ward + Language */}
      <Card className="bg-slate-900 border-slate-800 p-6">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="text-sm font-medium text-slate-300">
              Ward
            </label>

            <select
              value={ward}
              onChange={(e) => setWard(e.target.value)}
              className="w-full mt-2 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="anand_vihar">Anand Vihar</option>
              <option value="mandir_marg">Mandir Marg</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-300">
              Language
            </label>

            <div className="flex flex-wrap gap-2 mt-2">
              {[
                { code: "en", label: "English" },
                { code: "hi", label: "हिन्दी" },
                { code: "pa", label: "ਪੰਜਾਬੀ" },
                { code: "ur", label: "اردو" },
              ].map((lang) => (
                <Button
                  key={lang.code}
                  variant={language === lang.code ? "default" : "outline"}
                  onClick={() => changeLanguage(lang.code)}
                >
                  {lang.label}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Vulnerable Groups */}
      <Card className="bg-slate-900 border-slate-800 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Vulnerable Groups
        </h3>

        <div className="flex flex-wrap gap-3">
          <Badge className="bg-red-900 text-red-300 border-red-700" >Schools</Badge>
          <Badge className="bg-blue-900 text-blue-300 border-blue-700">Hospitals</Badge>
          <Badge className="bg-purple-900 text-purple-300 border-purple-700">Elderly</Badge>
          <Badge className="bg-green-900 text-green-300 border-green-700">Outdoor Workers</Badge>
        </div>
      </Card>

      {/* AI Advisory */}
      <Card className="bg-slate-900 border-slate-800 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          AI Generated Advisory
        </h3>

        <textarea
          rows={8}
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full rounded-lg border border-slate-700 bg-slate-800 p-4 text-white placeholder:text-slate-500 resize-none focus:outline-none focus:ring-2 focus:ring-cyan-500"
        />
        <p className="mt-3 text-sm text-slate-400">
          {advisory ? `${advisory.display.icon} · ${advisory.risk_level}` : error || "Generating advisory…"}
        </p>
      </Card>

      {/* Notification Preview */}
      <Card className="bg-slate-900 border-slate-800 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Push Notification Preview
        </h3>

        <div className="rounded-xl bg-slate-800 border border-slate-700 p-5">
          <p className="text-cyan-400 font-semibold">
            📢 UrbanAir AI Alert
          </p>

          <p className="mt-3 text-slate-200">
            {text}
          </p>
        </div>

        <Button className="w-full mt-6">
          <Send className="mr-2 h-5 w-5" />
          Publish Advisory
        </Button>
      </Card>
    </div>
  );
}