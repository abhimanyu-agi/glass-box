import { useQuery } from "@tanstack/react-query";
import {
  fetchKPIs,
  fetchTopStates,
  fetchWeatherImpact,
} from "@/lib/api";
import { useYear } from "@/contexts/YearContext";
import { fmtBig, fmtPct, fmtInt } from "@/lib/format";
import HeroStat from "@/components/HeroStat";
import StateProgressRow from "@/components/StateProgressRow";
import Eyebrow from "@/components/Eyebrow";
import EditorialSkeleton from "@/components/EditorialSkeleton";

export default function ReportsPage() {
  const { selectedYear } = useYear();

  const kpis = useQuery({
    queryKey: ["kpis", selectedYear],
    queryFn: () => fetchKPIs(selectedYear),
  });

  const states = useQuery({
    queryKey: ["states-report", selectedYear],
    queryFn: () => fetchTopStates(selectedYear, 5),
  });

  const weather = useQuery({
    queryKey: ["weather-report", selectedYear],
    queryFn: () => fetchWeatherImpact(selectedYear, 3),
  });

  const isLoading = kpis.isLoading || states.isLoading || weather.isLoading;

  // Build a one-line takeaway dynamically
  const buildHeadline = () => {
    if (!kpis.data) return "";
    const yoy = kpis.data.yoy_change_pct;
    const direction = yoy > 0 ? "rose" : yoy < 0 ? "fell" : "held steady";
    const magnitude = Math.abs(yoy).toFixed(1);
    return `Severe incidents ${direction} ${magnitude}% year over year, with the steepest concentration in five states.`;
  };

  // Top state for narrative
  const topState   = states.data?.[0];
  const topWeather = weather.data?.[0];
  const maxSevere  = states.data?.[0]?.severe_incidents ?? 1;

  return (
    <div className="overflow-y-auto h-full">
        <div className="max-w-[760px] mx-auto px-8 py-12">

      {isLoading || !kpis.data ? (
        <EditorialSkeleton />
      ) : (
        <article className="space-y-12">
          {/* HERO */}
          <header className="space-y-4">
            <Eyebrow>Safety Operations · {selectedYear}</Eyebrow>
            <h1 className="text-[34px] font-semibold tracking-tight text-foreground leading-[1.15]">
              {buildHeadline()}
            </h1>
            <p className="text-[16px] text-muted-foreground leading-[1.65] max-w-[600px]">
              Across millions of recorded incidents, {fmtBig(kpis.data.severe_incidents)} were classified
              as severe. {topState && `${topState.state} alone accounts for ${fmtInt(topState.severe_incidents)}.`}
              {" "}This briefing covers state concentration, weather drivers, and the year-over-year shift.
            </p>
          </header>

          {/* HERO STATS */}
          <div className="grid grid-cols-3 gap-0 border-y border-border py-7">
            <div className="border-r border-border pr-6">
              <HeroStat
                value={fmtBig(kpis.data.severe_incidents)}
                label="severe incidents"
              />
            </div>
            <div className="border-r border-border px-6">
              <HeroStat
                value={fmtPct(kpis.data.severe_rate_pct)}
                label="of all incidents"
              />
            </div>
            <div className="pl-6">
              <HeroStat
                value={fmtPct(kpis.data.yoy_change_pct, true)}
                label="vs prior year"
                tone={kpis.data.yoy_change_pct > 0 ? "danger" : "neutral"}
              />
            </div>
          </div>

          {/* SECTION: GEOGRAPHY */}
          <section className="space-y-4">
            <Eyebrow>Where incidents concentrate</Eyebrow>
            <h2 className="text-[22px] font-semibold tracking-tight text-foreground leading-[1.3]">
              Five states drive most of the severe incident volume.
            </h2>
            <p className="text-[15px] text-muted-foreground leading-[1.65]">
              {topState && (
                <>
                  {topState.state} leads with {fmtInt(topState.severe_incidents)} severe incidents — roughly{" "}
                  {(topState.severe_incidents / (kpis.data.severe_incidents || 1) * 100).toFixed(1)}% of the
                  national total. The next four states combined contribute another major share.
                </>
              )}
            </p>

            {states.data && (
              <div className="pt-2">
                {states.data.map((s, i) => (
                  <StateProgressRow
                    key={s.state}
                    state={s.state}
                    count={s.severe_incidents}
                    pctOfMax={(s.severe_incidents / maxSevere) * 100}
                    shadeIntensity={100 - i * 18}
                  />
                ))}
              </div>
            )}
          </section>

          {/* SECTION: WEATHER */}
          <section className="space-y-4">
            <Eyebrow>What drives severity</Eyebrow>
            <h2 className="text-[22px] font-semibold tracking-tight text-foreground leading-[1.3]">
              Weather is the largest preventable factor.
            </h2>
            <p className="text-[15px] text-muted-foreground leading-[1.65]">
              {topWeather && (
                <>
                  {topWeather.weather_condition} produces the highest severity rate at{" "}
                  {topWeather.severe_rate_pct.toFixed(1)}% — meaningfully above clear-day baselines.
                  Operations teams should consider weather-aware routing, dispatch, and driver alerting in
                  high-incidence regions.
                </>
              )}
            </p>

            {weather.data && (
              <div className="grid grid-cols-3 gap-4 pt-3">
                {weather.data.map((w) => (
                  <div
                    key={w.weather_condition}
                    className="bg-card border border-border rounded-lg p-4"
                  >
                    <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
                      {w.weather_condition}
                    </p>
                    <p className="text-2xl font-semibold tracking-tight text-foreground mt-2">
                      {w.severe_rate_pct.toFixed(1)}%
                    </p>
                    <p className="text-[11px] text-muted-foreground mt-1">
                      severity rate
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* CLOSING */}
          <section className="space-y-3 pt-2 border-t border-border">
            <Eyebrow>Recommended next steps</Eyebrow>
            <ul className="space-y-2 text-[15px] text-foreground leading-[1.65]">
              <li className="flex gap-3">
                <span className="text-muted-foreground shrink-0">01</span>
                <span>Investigate the {topState?.state} concentration with state-level operations leads.</span>
              </li>
              <li className="flex gap-3">
                <span className="text-muted-foreground shrink-0">02</span>
                <span>Review weather-aware routing protocols for {topWeather?.weather_condition.toLowerCase()} conditions.</span>
              </li>
              <li className="flex gap-3">
                <span className="text-muted-foreground shrink-0">03</span>
                <span>Compare current YoY trend against prior baseline before next quarterly review.</span>
              </li>
            </ul>
          </section>

          {/* FOOTER */}
          <footer className="pt-6 border-t border-border">
            <p className="text-[12px] text-muted-foreground italic">
              Generated from live operational data. For specific drill-downs, use the Dashboard view or the
              Ask AI assistant.
            </p>
          </footer>
        </article>
      )}
    </div>
  </div>
)
};