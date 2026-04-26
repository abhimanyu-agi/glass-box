import { cn } from "@/lib/utils";

interface Props {
  value: string;
  label: string;
  tone?: "neutral" | "danger";
}

export default function HeroStat({ value, label, tone = "neutral" }: Props) {
  return (
    <div>
      <p
        className={cn(
          "text-[40px] font-semibold tracking-tight leading-none",
          tone === "danger" ? "text-red-600 dark:text-red-400" : "text-foreground"
        )}
      >
        {value}
      </p>
      <p className="text-[13px] text-muted-foreground mt-2">{label}</p>
    </div>
  );
}