import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  LabelList,
} from "recharts";
import type { WeatherRow } from "@/lib/types";

interface Props { data: WeatherRow[]; }

export default function WeatherChart({ data }: Props) {
  const sorted = [...data].sort((a, b) => a.severe_rate_pct - b.severe_rate_pct);

  return (
    <div className="bg-card border border-border rounded-xl p-5 h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={sorted} layout="vertical" margin={{ top: 4, right: 48, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="hsl(var(--border))" horizontal={false} strokeDasharray="3 3" />
          <XAxis
            type="number"
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}%`}
          />
          <YAxis
            type="category"
            dataKey="weather_condition"
            tick={{ fontSize: 11, fill: "hsl(var(--foreground))" }}
            axisLine={false}
            tickLine={false}
            width={100}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--popover))",
              border: "1px solid hsl(var(--border))",
              borderRadius: 8,
              fontSize: 12,
              color: "hsl(var(--popover-foreground))",
            }}
            cursor={{ fill: "hsl(var(--muted))", opacity: 0.4 }}
            formatter={(v: number) => [`${v.toFixed(2)}%`, "Severity rate"]}
          />
          <Bar dataKey="severe_rate_pct" fill="#dc2626" radius={[0, 4, 4, 0]}>
            <LabelList
              dataKey="severe_rate_pct"
              position="right"
              style={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
              formatter={(v: number) => `${v.toFixed(1)}%`}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}