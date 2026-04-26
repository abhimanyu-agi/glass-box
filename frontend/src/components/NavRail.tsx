import { NavLink } from "react-router-dom";
import { LayoutDashboard, FileText, Settings, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/reports",   label: "Reports",   icon: FileText },
];

export default function NavRail() {
  return (
    <aside className="w-16 bg-card border-r border-border flex flex-col items-center py-4 gap-1.5 shrink-0">
      {/* Logo */}
      <div className="w-9 h-9 rounded-lg bg-brand-600 flex items-center justify-center shadow-sm shadow-brand-600/30 mb-3">
        <ShieldCheck className="w-5 h-5 text-white" />
      </div>

      {/* Nav items */}
      {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          title={label}
          className={({ isActive }) =>
            cn(
              "w-9 h-9 rounded-lg flex items-center justify-center transition group relative",
              isActive
                ? "bg-brand-50 text-brand-700 dark:bg-brand-600/15 dark:text-brand-300"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )
          }
        >
          <Icon className="w-4.5 h-4.5" strokeWidth={2} />
          {/* Tooltip on hover */}
          <span className="absolute left-full ml-3 px-2 py-1 rounded-md bg-foreground text-background text-xs font-medium opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap transition z-50">
            {label}
          </span>
        </NavLink>
      ))}

      {/* Spacer pushes settings to bottom */}
      <div className="flex-1" />

      {/* Settings (placeholder) */}
      <button
        title="Settings"
        className="w-9 h-9 rounded-lg flex items-center justify-center text-muted-foreground hover:bg-muted hover:text-foreground transition"
      >
        <Settings className="w-4.5 h-4.5" strokeWidth={2} />
      </button>
    </aside>
  );
}