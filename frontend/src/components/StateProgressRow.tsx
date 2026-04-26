import { fmtInt } from "@/lib/format";

interface Props {
  state: string;
  count: number;
  pctOfMax: number;   // 0-100
  shadeIntensity?: number;   // 0-100, controls darkness
}

export default function StateProgressRow({ state, count, pctOfMax, shadeIntensity = 100 }: Props) {
  // Use opacity to fade darker bars to lighter ones — tonal hierarchy
  const opacity = 0.4 + (shadeIntensity / 100) * 0.6;

  return (
    <div className="flex items-center gap-4 py-2.5 border-b border-border last:border-0">
      <p className="text-sm font-medium text-foreground w-10 shrink-0">{state}</p>
      <div className="flex-1 bg-muted rounded-full h-1.5 overflow-hidden">
        <div
          className="h-full bg-foreground rounded-full transition-all"
          style={{ width: `${pctOfMax}%`, opacity }}
        />
      </div>
      <p className="text-sm font-medium text-foreground tabular-nums w-16 text-right shrink-0">
        {fmtInt(count)}
      </p>
    </div>
  );
}