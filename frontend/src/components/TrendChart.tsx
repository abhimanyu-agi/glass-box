import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fmtMonthShort } from "@/lib/format";
import type { TrendPoint } from "@/lib/types";

interface Props { data: TrendPoint[]; }

export default function TrendChart({ data }: Props) {
  return (
    <div className="bg-card border border-border rounded-xl p-5 h-[320px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
          <defs>
            <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stopColor="#4f46e5" stopOpacity={0.18} />
              <stop offset="100%" stopColor="#4f46e5" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="hsl(var(--border))" vertical={false} strokeDasharray="3 3" />
          <XAxis
            dataKey="incident_month"
            tickFormatter={fmtMonthShort}
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            axisLine={false}
            tickLine={false}
            interval="preserveStartEnd"
            minTickGap={28}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(0)}k` : `${v}`)}
            width={48}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--popover))",
              border: "1px solid hsl(var(--border))",
              borderRadius: 8,
              fontSize: 12,
              color: "hsl(var(--popover-foreground))",
            }}
            labelStyle={{ color: "hsl(var(--muted-foreground))", fontSize: 11 }}
            formatter={(value: number, name: string) => [value.toLocaleString(), name]}
            labelFormatter={(label: string) => fmtMonthShort(label)}
          />
          <Area
            type="monotone"
            dataKey="total_incidents"
            name="Total"
            stroke="#4f46e5"
            strokeWidth={2}
            fill="url(#totalGrad)"
          />
          <Line
            type="monotone"
            dataKey="severe_incidents"
            name="Severe"
            stroke="#dc2626"
            strokeWidth={2}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}