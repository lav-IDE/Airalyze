import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Send } from "lucide-react";
import { getAdvisory, publishAdvisory } from "@/services/api";

export default function AdvisoryGenerator() {
  const [ward, setWard] = useState("anand_vihar");
  const [language, setLanguage] = useState("en");
  const [text, setText] = useState("");
  const [advisory, setAdvisory] = useState(null);
  const [error, setError] = useState("");
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishFeedback, setPublishFeedback] = useState(null);

  const handlePublish = () => {
    setIsPublishing(true);
    setPublishFeedback(null);
    publishAdvisory(ward, language, profile, text)
      .then((res) => {
        setPublishFeedback({ type: "success", message: res.message || "Advisory published successfully!" });
      })
      .catch((err) => {
        setPublishFeedback({ type: "error", message: err.message || "Failed to publish advisory." });
      })
      .finally(() => {
        setIsPublishing(false);
      });
  };

  const [profile, setProfile] = useState({
    age_group: "adult",
    health_conditions: ["none"],
    activity: "indoor",
  });

  const updateProfile = (name, value) => {
    setProfile((current) => ({
      ...current,
      [name]: name === "health_conditions" ? [value] : value,
    }));
  };

  const isSchoolsActive = profile.age_group === "child";
  const isHospitalsActive = profile.health_conditions.some((c) =>
    ["asthma", "heart_disease", "pregnant"].includes(c)
  );
  const isElderlyActive = profile.age_group === "elderly";
  const isOutdoorActive = profile.activity === "outdoor_worker";

  function changeLanguage(lang) {
    setLanguage(lang);
  }

  const ageGroup = profile.age_group;
  const healthCondition = profile.health_conditions[0];
  const activityProfile = profile.activity;

  useEffect(() => {
    let cancelled = false;
    setError("");
    setPublishFeedback(null);
    getAdvisory(ward, {
      age_group: ageGroup,
      health_conditions: [healthCondition],
      activity: activityProfile,
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
  }, [ward, language, ageGroup, healthCondition, activityProfile]);

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

      {/* Target Demographic & Vulnerability Groups */}
      <Card className="bg-slate-900 border-slate-800 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Target Demographic & Vulnerability Groups
        </h3>

        {/* Profile Selectors */}
        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Age Group
            </label>
            <select
              value={profile.age_group}
              onChange={(e) => updateProfile("age_group", e.target.value)}
              className="w-full mt-2 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="child">Child</option>
              <option value="adult">Adult</option>
              <option value="elderly">Older adult</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Health Consideration
            </label>
            <select
              value={profile.health_conditions[0]}
              onChange={(e) => updateProfile("health_conditions", e.target.value)}
              className="w-full mt-2 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="none">No condition</option>
              <option value="asthma">Asthma</option>
              <option value="heart_disease">Heart condition</option>
              <option value="pregnant">Pregnant</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Activity Profile
            </label>
            <select
              value={profile.activity}
              onChange={(e) => updateProfile("activity", e.target.value)}
              className="w-full mt-2 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="indoor">Mostly indoors</option>
              <option value="commuter">Commuter</option>
              <option value="outdoor_worker">Outdoor work</option>
              <option value="exercise_planned">Exercise planned</option>
            </select>
          </div>
        </div>

        {/* Vulnerable Group Badges */}
        <div className="border-t border-slate-800 pt-5">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Targeted Vulnerability Groups
          </h4>
          <div className="flex flex-wrap gap-3">
            <Badge className={`transition-all duration-300 ${isSchoolsActive ? "bg-red-900 text-red-300 border-red-700 scale-105 font-bold" : "bg-slate-850 text-slate-600 border-slate-800 opacity-40"}`}>Schools</Badge>
            <Badge className={`transition-all duration-300 ${isHospitalsActive ? "bg-blue-900 text-blue-300 border-blue-700 scale-105 font-bold" : "bg-slate-850 text-slate-600 border-slate-800 opacity-40"}`}>Hospitals</Badge>
            <Badge className={`transition-all duration-300 ${isElderlyActive ? "bg-purple-900 text-purple-300 border-purple-700 scale-105 font-bold" : "bg-slate-850 text-slate-600 border-slate-800 opacity-40"}`}>Elderly</Badge>
            <Badge className={`transition-all duration-300 ${isOutdoorActive ? "bg-green-900 text-green-300 border-green-700 scale-105 font-bold" : "bg-slate-850 text-slate-600 border-slate-800 opacity-40"}`}>Outdoor Workers</Badge>
          </div>
        </div>

        {/* Special Advisories */}
        {(isSchoolsActive || isHospitalsActive || isElderlyActive || isOutdoorActive) && (
          <div className="mt-5 p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-3">
            <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
              Special Administrative Advisory Actions
            </div>
            <div className="space-y-3 text-sm text-slate-200">
              {isSchoolsActive && (
                <div className="flex items-start gap-2">
                  <span className="text-red-400 mt-0.5">🏫</span>
                  <div>
                    <strong className="text-red-300">School Action Alert:</strong> Suspend outdoor sports, close classroom windows during peak hours, and advise student parents.
                  </div>
                </div>
              )}
              {isHospitalsActive && (
                <div className="flex items-start gap-2">
                  <span className="text-blue-400 mt-0.5">🏥</span>
                  <div>
                    <strong className="text-blue-300">Healthcare Alert:</strong> Distribute respiratory guidelines to clinics and ensure adequate stocks of bronchodilators/oxygen.
                  </div>
                </div>
              )}
              {isElderlyActive && (
                <div className="flex items-start gap-2">
                  <span className="text-purple-400 mt-0.5">👵</span>
                  <div>
                    <strong className="text-purple-300">Senior Care Alert:</strong> Contact senior recreation centers and care homes to restrict outdoor activities and run air filtration.
                  </div>
                </div>
              )}
              {isOutdoorActive && (
                <div className="flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">👷</span>
                  <div>
                    <strong className="text-green-300">Labor Welfare Alert:</strong> Direct contractors to provide N95 masks, enforce rest intervals, and limit shifts in critical AQI zones.
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
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
            📢 Airalyze AI Alert
          </p>

          <p className="mt-3 text-slate-200">
            {text}
          </p>
        </div>

        {publishFeedback && (
          <div className={`mt-4 p-3 rounded-lg text-sm font-semibold border ${publishFeedback.type === "success" ? "bg-green-950 text-green-300 border-green-800" : "bg-red-950 text-red-300 border-red-800"}`}>
            {publishFeedback.message}
          </div>
        )}

        <Button onClick={handlePublish} disabled={isPublishing || !text} className="w-full mt-6">
          <Send className="mr-2 h-5 w-5" />
          {isPublishing ? "Publishing…" : "Publish Advisory"}
        </Button>
      </Card>
    </div>
  );
}