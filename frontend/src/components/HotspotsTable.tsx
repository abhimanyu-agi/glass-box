import type { CityRow } from "@/lib/types";
import { fmtInt } from "@/lib/format";

interface Props { data: CityRow[]; }

export default function HotspotsTable({ data }: Props) {
  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-muted/30">
            <th className="text-left  font-medium text-muted-foreground px-4 py-2.5 text-[11px] uppercase tracking-wider w-12">#</th>
            <th className="text-left  font-medium text-muted-foreground px-4 py-2.5 text-[11px] uppercase tracking-wider">State</th>
            <th className="text-left  font-medium text-muted-foreground px-4 py-2.5 text-[11px] uppercase tracking-wider">City</th>
            <th className="text-right font-medium text-muted-foreground px-4 py-2.5 text-[11px] uppercase tracking-wider">Total</th>
            <th className="text-right font-medium text-muted-foreground px-4 py-2.5 text-[11px] uppercase tracking-wider">Severe</th>
            <th className="text-right font-medium text-muted-foreground px-4 py-2.5 text-[11px] uppercase tracking-wider">Critical</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={`${row.state}-${row.city}`} className="border-b border-border last:border-0 hover:bg-muted/30 transition">
              <td className="px-4 py-2.5 text-muted-foreground tabular-nums">{i + 1}</td>
              <td className="px-4 py-2.5 text-foreground font-medium">{row.state}</td>
              <td className="px-4 py-2.5 text-foreground">{row.city}</td>
              <td className="px-4 py-2.5 text-foreground text-right tabular-nums">{fmtInt(row.total_incidents)}</td>
              <td className="px-4 py-2.5 text-foreground text-right tabular-nums">{fmtInt(row.severe_incidents)}</td>
              <td className="px-4 py-2.5 text-foreground text-right tabular-nums">{fmtInt(row.critical_incidents)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}