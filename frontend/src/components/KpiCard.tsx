import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string;
  delta?: string | null;
  deltaTone?: "neutral" | "good" | "bad";
  loading?: boolean;
}

export default function KpiCard({
  label,
  value,
  delta,
  deltaTone = "neutral",
  loading = false,
}: KpiCardProps) {
  return (
    <div className="bg-card border border-border rounded-xl p-5 transition hover:shadow-sm">
      <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-[0.08em]">
        {label}
      </p>
      {loading ? (
        <div className="mt-3 h-9 w-24 bg-muted rounded animate-pulse" />
      ) : (
        <p className="text-3xl font-semibold tracking-tight text-foreground mt-2 leading-none">
          {value}
        </p>
      )}
      {delta && !loading && (
        <p
          className={cn(
            "text-xs font-medium mt-2",
            deltaTone === "good" && "text-emerald-600 dark:text-emerald-400",
            deltaTone === "bad"  && "text-red-600 dark:text-red-400",
            deltaTone === "neutral" && "text-muted-foreground"
          )}
        >
          {delta}
        </p>
      )}
    </div>
  );
}