export function fmtBig(n: number | null | undefined): string {
  if (n == null) return "—";
  const abs = Math.abs(n);
  if (abs >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (abs >= 1_000)     return `${(n / 1_000).toFixed(0)}K`;
  return n.toLocaleString();
}

export function fmtPct(n: number | null | undefined, signed = false): string {
  if (n == null) return "—";
  const sign = signed && n > 0 ? "+" : "";
  return `${sign}${n.toFixed(1)}%`;
}

export function fmtInt(n: number | null | undefined): string {
  if (n == null) return "—";
  return n.toLocaleString();
}

export function fmtMonthShort(iso: string): string {
  // "2022-08-01" → "Aug 22"
  const d = new Date(iso);
  const month = d.toLocaleString("en-US", { month: "short" });
  const year = String(d.getFullYear()).slice(2);
  return `${month} ${year}`;
}