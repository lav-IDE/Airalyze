import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Send } from "lucide-react";

const advisories = {
  English:
    "AQI is expected to reach VERY POOR levels over the next 24 hours. Children, elderly citizens, and people with respiratory illnesses should avoid prolonged outdoor exposure. Schools are advised to limit outdoor activities.",

  Hindi:
    "अगले 24 घंटों में वायु गुणवत्ता 'बहुत खराब' श्रेणी में रहने की संभावना है। बच्चों, बुजुर्गों और श्वसन रोगियों को लंबे समय तक बाहर रहने से बचना चाहिए। स्कूलों को बाहरी गतिविधियाँ सीमित करने की सलाह दी जाती है。",
};

export default function AdvisoryGenerator() {
  const [ward, setWard] = useState("Anand Vihar");
  const [language, setLanguage] = useState("English");
  const [text, setText] = useState(advisories.English);

  function changeLanguage(lang) {
    setLanguage(lang);
    setText(advisories[lang]);
  }

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
              <option>Anand Vihar</option>
              <option>Mandir Marg</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-300">
              Language
            </label>

            <div className="flex gap-3 mt-2">
              <Button
                variant={language === "English" ? "default" : "outline"}
                onClick={() => changeLanguage("English")}
              >
                English
              </Button>

              <Button
                variant={language === "Hindi" ? "default" : "outline"}
                onClick={() => changeLanguage("Hindi")}
              >
                हिन्दी
              </Button>
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