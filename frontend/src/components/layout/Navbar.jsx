import { MapPin } from "lucide-react";
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between border-b border-slate-800 bg-slate-950 px-8 py-5">
      <div>
        <h1 className="text-2xl font-bold text-white">
          Airalyze
        </h1>
        <p className="text-sm text-slate-400">
          Hyperlocal Air Quality Intelligence
        </p>
      </div>

      <Link to="/admin/login">

        <button className="bg-cyan-500 hover:bg-cyan-600 px-5 py-2 rounded-lg text-black font-semibold transition">

          Municipal Login

        </button>

      </Link>
      
      <div className="flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-slate-300">
        <MapPin size={18} />
        Delhi
      </div>
    </nav>
  );
}