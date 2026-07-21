import { useState, useEffect } from "react";

import Navbar from "@/components/layout/Navbar";

import CityMap from "@/components/overview/CityMap";
import AQISummary from "@/components/overview/AQISummary";

import WardSelector from "@/components/forecast/WardSelector";
import FeatureImportance from "@/components/forecast/FeatureImportance";
import ForecastSignal from "@/components/forecast/ForecastSignal";
import MetricsCard from "@/components/forecast/MetricsCard";
import ArchitectureDiagram from "@/components/architecture/ArchitectureDiagram";
import AdvisoryCard from "@/components/advisory/AdvisoryCard";

import { getForecast, getWards } from "@/services/api";

const WARD_STORAGE_KEY = "urbanair:selected-ward";

export default function Dashboard() {
  const [selectedWardId, setSelectedWardId] = useState(() => localStorage.getItem(WARD_STORAGE_KEY));
  const [wards, setWards] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [forecastError, setForecastError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getWards().then((loadedWards) => {
      setWards(loadedWards);
      if (selectedWardId && !loadedWards.some((ward) => ward.id === selectedWardId)) {
        localStorage.removeItem(WARD_STORAGE_KEY);
        setSelectedWardId(null);
      }
    }).catch((error) => console.error("Unable to load wards:", error));
  }, []);

  useEffect(() => {
    if (!selectedWardId) {
      setForecast(null);
      setForecastError(null);
      setIsLoading(false);
      return;
    }
    let cancelled = false;
    setIsLoading(true);
    setForecast(null);
    setForecastError(null);
    getForecast(selectedWardId)
      .then((result) => { if (!cancelled) setForecast(result); })
      .catch((error) => { if (!cancelled) setForecastError(error.message || "Forecast temporarily unavailable"); })
      .finally(() => { if (!cancelled) setIsLoading(false); });
    return () => { cancelled = true; };
  }, [selectedWardId]);

  const selectedWard = wards.find((ward) => ward.id === selectedWardId);
  const changeWard = (wardId) => {
    if (wardId) localStorage.setItem(WARD_STORAGE_KEY, wardId);
    else localStorage.removeItem(WARD_STORAGE_KEY);
    setSelectedWardId(wardId);
  };

  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />

      <main className="max-w-7xl mx-auto p-8 space-y-8">

        <WardSelector
          wards={wards}
          selectedWardId={selectedWardId}
          setSelectedWard={changeWard}
        />

        {!selectedWard ? (
          <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900 p-10 text-center text-slate-300">
            Select your ward to view its current 1-hour AQI forecast, health advisory, and model drivers.
          </div>
        ) : <>
        <div className="space-y-6">
          <CityMap
    ward={selectedWard}
    forecast={forecast}
    error={forecastError}
    isLoading={isLoading}
/>
          <AQISummary
    forecast={forecast}
    selectedWard={selectedWard.name}
    error={forecastError}
    isLoading={isLoading}
/>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <FeatureImportance
              selectedWard={selectedWard.name}
              forecast={forecast}
              error={forecastError}
              isLoading={isLoading}
            />
          </div>
          <ForecastSignal
            forecast={forecast}
            error={forecastError}
            isLoading={isLoading}
          />
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 items-stretch">
          <div>
            <MetricsCard
              forecast={forecast}
              selectedWard={selectedWard.name}
              error={forecastError}
              isLoading={isLoading}
            />
          </div>
          <AdvisoryCard
            ward={selectedWard}
            forecast={forecast}
          />

        </div>

        <ArchitectureDiagram />
        </>}

      </main>
    </div>
  );
}
