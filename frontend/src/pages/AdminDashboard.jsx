import AdminSidebar from "@/components/admin/AdminSidebar";

import DashboardHeader from "@/components/admin/DashboardHeader";
import WardOverview from "@/components/admin/WardOverview";
import AdvisoryGenerator from "@/components/admin/AdvisoryGenerator";

export default function AdminDashboard() {
  return (
    <div className="flex bg-slate-950 text-white">

      <AdminSidebar />

      <main className="flex-1 p-8 overflow-y-auto h-screen">

        <DashboardHeader />

        <div className="grid grid-cols-12 gap-6 mt-8">

          <div className="col-span-3">

            <WardOverview />

          </div>

          <div className="col-span-9">

            <AdvisoryGenerator />

          </div>

        </div>

      </main>

    </div>
  );
}