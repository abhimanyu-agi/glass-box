import { useLocation } from "react-router-dom";
import YearSelector from "./YearSelector";
import UserMenu from "./UserMenu";

const TITLES: Record<string, { title: string; subtitle: string }> = {
  "/dashboard": {
    title: "Dashboard",
    subtitle: "US road incidents · Live data through March 2023",
  },
  "/reports": {
    title: "Reports",
    subtitle: "Editorial briefings on safety performance",
  },
};

export default function AppHeader() {
  const { pathname } = useLocation();
  const meta = TITLES[pathname] || { title: "Safety Operations", subtitle: "" };
  const showYearSelector = pathname === "/dashboard" || pathname === "/reports";

  return (
    <header className="h-16 px-6 border-b border-border bg-background flex items-center justify-between shrink-0">
      <div className="min-w-0">
        <h1 className="text-lg font-semibold tracking-tight text-foreground leading-tight truncate">
          {meta.title}
        </h1>
        {meta.subtitle && (
          <p className="text-xs text-muted-foreground truncate">{meta.subtitle}</p>
        )}
      </div>

      <div className="flex items-center gap-3 shrink-0">
        {showYearSelector && <YearSelector />}
        <UserMenu />
      </div>
    </header>
  );
}