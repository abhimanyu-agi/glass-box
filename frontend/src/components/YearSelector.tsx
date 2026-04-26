import { useQuery } from "@tanstack/react-query";
import { ChevronDown, Calendar } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { fetchAvailableYears } from "@/lib/api";
import { useYear } from "@/contexts/YearContext";
import { cn } from "@/lib/utils";

export default function YearSelector() {
  const { selectedYear, setSelectedYear } = useYear();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const { data: years = [] } = useQuery({
    queryKey: ["available-years"],
    queryFn: fetchAvailableYears,
  });

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-border bg-card hover:bg-muted transition text-sm font-medium text-foreground"
      >
        <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
        {selectedYear}
        <ChevronDown className={cn("w-3.5 h-3.5 text-muted-foreground transition", open && "rotate-180")} />
      </button>

      {open && years.length > 0 && (
        <div className="absolute right-0 top-full mt-1 w-32 bg-popover border border-border rounded-md shadow-lg py-1 z-40">
          {years.map((y) => (
            <button
              key={y}
              onClick={() => { setSelectedYear(y); setOpen(false); }}
              className={cn(
                "w-full px-3 py-1.5 text-sm text-left hover:bg-muted transition",
                y === selectedYear ? "text-brand-700 dark:text-brand-300 font-medium" : "text-foreground"
              )}
            >
              {y}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}