import {
  LayoutDashboard,
  Megaphone,
  LogOut,
} from "lucide-react";

const items = [
  {
    icon: LayoutDashboard,
    title: "Dashboard",
    active: true,
  },
  {
    icon: Megaphone,
    title: "Issue Advisory",
  },
];

export default function AdminSidebar() {
  return (
    <div className="w-72 bg-slate-900 border-r border-slate-800 h-screen flex flex-col justify-between">

      <div>

        <div className="p-6 border-b border-slate-800">

          <h1 className="text-2xl font-bold text-cyan-400">
            Airalyze
          </h1>

          <p className="text-slate-400 text-sm mt-2">
            Municipal Command Center
          </p>

        </div>

        <div className="p-4 space-y-2">

          {items.map((item) => {

            const Icon = item.icon;

            return (

              <button
                key={item.title}
                className={`w-full flex items-center gap-4 rounded-xl px-4 py-3 transition

                ${
                  item.active
                    ? "bg-cyan-500 text-black"
                    : "hover:bg-slate-800 text-slate-300"
                }`}
              >

                <Icon size={20} />

                {item.title}

              </button>

            );

          })}

        </div>

      </div>

      <div className="p-6 border-t border-slate-800">

        <button className="flex items-center gap-3 text-red-400">

          <LogOut size={18} />

          Logout

        </button>

      </div>

    </div>
  );
}