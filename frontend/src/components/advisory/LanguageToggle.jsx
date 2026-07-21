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

      <div className="flex gap-4">

        <button
          onClick={() => setLanguage("English")}
          className={`px-5 py-2 rounded-lg transition-all
            ${
              language === "English"
                ? "bg-cyan-500 text-black font-semibold"
                : "bg-slate-700 hover:bg-slate-600"
            }`}
        >
          English
        </button>

        <button
          onClick={() => setLanguage("Hindi")}
          className={`px-5 py-2 rounded-lg transition-all
            ${
              language === "Hindi"
                ? "bg-cyan-500 text-black font-semibold"
                : "bg-slate-700 hover:bg-slate-600"
            }`}
        >
          हिन्दी
        </button>

      </div>

    </div>
  );
}