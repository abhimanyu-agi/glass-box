export default function EditorialSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="space-y-3">
        <div className="h-3 w-32 bg-muted rounded" />
        <div className="h-9 w-full bg-muted rounded" />
        <div className="h-9 w-2/3 bg-muted rounded" />
      </div>
      <div className="h-px bg-border" />
      <div className="grid grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="space-y-2">
            <div className="h-9 w-24 bg-muted rounded" />
            <div className="h-3 w-32 bg-muted rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}