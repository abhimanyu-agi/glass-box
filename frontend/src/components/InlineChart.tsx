import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ChartPayload } from "@/hooks/useChatStream";
import { fmtInt } from "@/lib/format";

interface Props { chart: ChartPayload; }

const BAR_COLORS = ["#4f46e5", "#6366f1", "#818cf8", "#a5b4fc", "#c7d2fe"];

export default function InlineChart({ chart }: Props) {
  if (!chart.records || chart.records.length === 0) return null;

  // Auto-detect axes — first column is label, last numeric column is value
  const labelKey = chart.columns[0];
  const valueKey =
    chart.columns.find(
      (c) =>
        c !== labelKey &&
        chart.records[0][c] != null &&
        typeof chart.records[0][c] === "number"
    ) || chart.columns[1] || chart.columns[0];

  const isLine = chart.type === "line" || chart.type === "trend";

  if (isLine) {
    return (
      <div className="h-[200px] -mx-1 mt-3">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chart.records} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
            <CartesianGrid stroke="hsl(var(--border))" vertical={false} strokeDasharray="3 3" />
            <XAxis
              dataKey={labelKey}
              tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
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
            />
            <Line type="monotone" dataKey={valueKey} stroke="#4f46e5" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // Default: bar chart (vertical bars for short label lists)
  const isHorizontal = chart.records.length > 6;

  return (
    <div className={`-mx-1 mt-3 ${isHorizontal ? "h-[260px]" : "h-[200px]"}`}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chart.records}
          layout={isHorizontal ? "vertical" : "horizontal"}
          margin={{ top: 4, right: isHorizontal ? 36 : 8, left: isHorizontal ? 0 : -12, bottom: 0 }}
        >
          <CartesianGrid
            stroke="hsl(var(--border))"
            horizontal={!isHorizontal}
            vertical={isHorizontal}
            strokeDasharray="3 3"
          />
          {isHorizontal ? (
            <>
              <XAxis
                type="number"
                tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey={labelKey}
                tick={{ fontSize: 10, fill: "hsl(var(--foreground))" }}
                axisLine={false}
                tickLine={false}
                width={70}
              />
            </>
          ) : (
            <>
              <XAxis
                dataKey={labelKey}
                tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
                axisLine={false}
                tickLine={false}
                width={32}
              />
            </>
          )}
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--popover))",
              border: "1px solid hsl(var(--border))",
              borderRadius: 8,
              fontSize: 12,
              color: "hsl(var(--popover-foreground))",
            }}
            cursor={{ fill: "hsl(var(--muted))", opacity: 0.4 }}
            formatter={(v: any) => [typeof v === "number" ? fmtInt(v) : v, valueKey]}
          />
          <Bar dataKey={valueKey} radius={isHorizontal ? [0, 4, 4, 0] : [4, 4, 0, 0]}>
            {chart.records.map((_, i) => (
              <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}