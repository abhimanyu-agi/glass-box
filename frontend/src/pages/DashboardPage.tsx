import { useQuery } from "@tanstack/react-query";
import {
  fetchHotspots,
  fetchKPIs,
  fetchTopStates,
  fetchTrend,
  fetchWeatherImpact,
} from "@/lib/api";
import { useYear } from "@/contexts/YearContext";
import { fmtBig, fmtPct } from "@/lib/format";
import KpiCard from "@/components/KpiCard";
import SectionTitle from "@/components/SectionTitle";
import TrendChart from "@/components/TrendChart";
import StatesChart from "@/components/StatesChart";
import WeatherChart from "@/components/WeatherChart";
import HotspotsTable from "@/components/HotspotsTable";
import ChartSkeleton from "@/components/ChartSkeleton";
import AskAIRail from "@/components/AskAIRail";
import { Sparkles } from "lucide-react";
import { useRail } from "@/contexts/RailContext";

export default function DashboardPage() {
  const { selectedYear } = useYear();

  const kpis = useQuery({
    queryKey: ["kpis", selectedYear],
    queryFn: () => fetchKPIs(selectedYear),
  });

  const trend = useQuery({
    queryKey: ["trend", 24],
    queryFn: () => fetchTrend(24),
  });

  const states = useQuery({
    queryKey: ["states", selectedYear],
    queryFn: () => fetchTopStates(selectedYear, 10),
  });

  const weather = useQuery({
    queryKey: ["weather", selectedYear],
    queryFn: () => fetchWeatherImpact(selectedYear, 10),
  });

const hotspots = useQuery({
    queryKey: ["hotspots", selectedYear],
    queryFn: () => fetchHotspots(selectedYear, 15),
  });

  const { railOpen, openRail } = useRail();

  return (
    <div className="flex h-full">
      {/* Main scrollable area */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6 space-y-6 max-w-[1400px] mx-auto">

          {/* Toolbar — only visible when rail is closed */}
          {!railOpen && (
            <div className="flex justify-end">
              <button
                onClick={openRail}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium shadow-sm shadow-brand-600/25 transition group"
              >
                <Sparkles className="w-3.5 h-3.5" />
                Ask AI
                <kbd className="hidden sm:inline-flex items-center px-1 py-0 text-[10px] font-mono text-white/80 border border-white/30 rounded ml-1">
                  ⌘K
                </kbd>
              </button>
            </div>
          )}

          {/* KPI row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <KpiCard
          label="Total Incidents"
          value={kpis.data ? fmtBig(kpis.data.total_incidents) : "—"}
          loading={kpis.isLoading}
        />
        <KpiCard
          label="Severe Incidents"
          value={kpis.data ? fmtBig(kpis.data.severe_incidents) : "—"}
          loading={kpis.isLoading}
        />
        <KpiCard
          label="Severity Rate"
          value={kpis.data ? fmtPct(kpis.data.severe_rate_pct) : "—"}
          loading={kpis.isLoading}
        />
        <KpiCard
          label="YoY Change"
          value={kpis.data ? fmtPct(kpis.data.yoy_change_pct, true) : "—"}
          deltaTone={
            kpis.data && kpis.data.yoy_change_pct > 0 ? "bad" :
            kpis.data && kpis.data.yoy_change_pct < 0 ? "good" : "neutral"
          }
          loading={kpis.isLoading}
        />
      </div>

      {/* Trend */}
      <section>
        <SectionTitle title="Monthly trend" subtitle="Total and severe incidents over the last 24 months" />
        {trend.isLoading || !trend.data
          ? <ChartSkeleton height={320} />
          : <TrendChart data={trend.data} />}
      </section>

      {/* States + Weather */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <section>
          <SectionTitle title="Top 10 states" subtitle={`Severe incidents · ${selectedYear}`} />
          {states.isLoading || !states.data
            ? <ChartSkeleton height={400} />
            : <StatesChart data={states.data} />}
        </section>
        <section>
          <SectionTitle title="Weather impact" subtitle="Severity rate by weather condition" />
          {weather.isLoading || !weather.data
            ? <ChartSkeleton height={400} />
            : <WeatherChart data={weather.data} />}
        </section>
      </div>

      {/* Hotspots */}
      <section>
        <SectionTitle title="Accident hotspots" subtitle="Top 15 cities by severe incidents" />
        {hotspots.isLoading || !hotspots.data
          ? <ChartSkeleton height={460} />
          : <HotspotsTable data={hotspots.data} />}
      </section>
        </div>
      </div>

      {/* Right rail */}
      <AskAIRail />
    </div>
  );
}