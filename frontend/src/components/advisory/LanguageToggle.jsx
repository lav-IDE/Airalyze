import { Languages } from "lucide-react";

export default function LanguageToggle({
  language,
  setLanguage,
}) {
  return (
    <div className="rounded-xl bg-slate-800 p-5">

      <div className="flex items-center gap-3 mb-4">
        <Languages className="text-cyan-400" />
        <h3 className="font-semibold text-lg">
          Advisory Language
        </h3>
      </div>

      <div className="flex flex-wrap gap-2">
        {[
          { code: "en", label: "English" },
          { code: "hi", label: "हिन्दी" },
          { code: "pa", label: "ਪੰਜਾਬੀ" },
          { code: "ur", label: "اردو" },
        ].map((lang) => (
          <button
            key={lang.code}
            onClick={() => setLanguage(lang.code)}
            className={`px-4 py-2 rounded-lg transition-all ${
              language === lang.code
                ? "bg-cyan-500 text-black font-semibold"
                : "bg-slate-700 hover:bg-slate-600 text-white"
            }`}
          >
            {lang.label}
          </button>
        ))}
      </div>

    </div>
  );
}