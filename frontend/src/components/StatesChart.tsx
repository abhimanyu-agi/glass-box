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
import type { StateRow } from "@/lib/types";

interface Props { data: StateRow[]; }

export default function StatesChart({ data }: Props) {
  // Recharts horizontal bars — sort ascending so largest is at top
  const sorted = [...data].sort((a, b) => a.severe_incidents - b.severe_incidents);

  return (
    <div className="bg-card border border-border rounded-xl p-5 h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={sorted} layout="vertical" margin={{ top: 4, right: 40, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="hsl(var(--border))" horizontal={false} strokeDasharray="3 3" />
          <XAxis
            type="number"
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(0)}k` : `${v}`)}
          />
          <YAxis
            type="category"
            dataKey="state"
            tick={{ fontSize: 12, fill: "hsl(var(--foreground))", fontWeight: 500 }}
            axisLine={false}
            tickLine={false}
            width={32}
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
            formatter={(v: number) => [v.toLocaleString(), "Severe"]}
          />
          <Bar dataKey="severe_incidents" fill="#4f46e5" radius={[0, 4, 4, 0]}>
            <LabelList
              dataKey="severe_incidents"
              position="right"
              style={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
              formatter={(v: number) => v.toLocaleString()}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}