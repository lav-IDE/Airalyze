import { Card } from "@/components/ui/card";

const wards = [
  {
    name: "Anand Vihar",
    aqi: 248,
    status: "Critical",
    color: "bg-red-500",
  },
  {
    name: "Mandir Marg",
    aqi: 162,
    status: "Moderate",
    color: "bg-yellow-500",
  },
];

export default function WardOverview() {
  return (
    <Card className="bg-slate-900 border-slate-800 p-6">

      <h2 className="text-xl font-semibold mb-6 text-white">
        Critical Wards
      </h2>

      <div className="space-y-4">

        {wards.map((ward) => (

          <div
            key={ward.name}
            className="rounded-xl bg-slate-800 p-4"
          >

            <div className="flex justify-between">

              <h3 className="text-white">{ward.name}</h3>

              <span
                className={`w-3 h-3 rounded-full ${ward.color}`}
              />

            </div>

            <p className="mt-3 text-3xl font-bold text-white">
              {ward.aqi}
            </p>

            <p className="text-slate-400">
              {ward.status}
            </p>

          </div>

        ))}

      </div>

    </Card>
  );
}   