interface Props { height?: number | string; }

export default function ChartSkeleton({ height = 320 }: Props) {
  return (
    <div
      className="bg-card border border-border rounded-xl p-5 animate-pulse flex items-end gap-2"
      style={{ height }}
    >
      {Array.from({ length: 12 }).map((_, i) => (
        <div
          key={i}
          className="flex-1 bg-muted rounded-sm"
          style={{ height: `${30 + Math.sin(i) * 30 + i * 4}%` }}
        />
      ))}
    </div>
  );
}