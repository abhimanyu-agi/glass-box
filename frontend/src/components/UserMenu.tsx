import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Sun, Moon, LogOut, ChevronDown, KeyRound } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { cn } from "@/lib/utils";
import ChangePasswordDialog from "./ChangePasswordDialog";

function initials(name: string | null, fallback: string): string {
  if (!name) return fallback.slice(0, 2).toUpperCase();
  return name
    .split(" ")
    .map((s) => s[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export default function UserMenu() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
    const [open, setOpen] = useState(false);
  const [pwdOpen, setPwdOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on click outside
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  if (!user) return null;

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 pr-2 pl-1 py-1 rounded-full hover:bg-muted transition"
      >
        <div className="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-600/20 text-brand-700 dark:text-brand-300 text-xs font-semibold flex items-center justify-center">
          {initials(user.full_name, user.username)}
        </div>
        <ChevronDown
          className={cn(
            "w-3.5 h-3.5 text-muted-foreground transition",
            open && "rotate-180"
          )}
        />
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-56 bg-popover border border-border rounded-lg shadow-lg py-1 z-50">
          <div className="px-3 py-2 border-b border-border">
            <p className="text-sm font-medium text-foreground truncate">
              {user.full_name || user.username}
            </p>
            <p className="text-xs text-muted-foreground truncate">
              {user.email || `Role: ${user.role}`}
            </p>
          </div>

          <button
            onClick={() => {
              toggleTheme();
            }}
            className="w-full px-3 py-2 flex items-center gap-2 text-sm text-foreground hover:bg-muted transition text-left"
          >
            {theme === "light" ? (
              <Moon className="w-4 h-4 text-muted-foreground" />
            ) : (
              <Sun className="w-4 h-4 text-muted-foreground" />
            )}
            {theme === "light" ? "Dark mode" : "Light mode"}
          </button>

          <button
            onClick={() => {
              setOpen(false);
              setPwdOpen(true);
            }}
            className="w-full px-3 py-2 flex items-center gap-2 text-sm text-foreground hover:bg-muted transition text-left"
          >
            <KeyRound className="w-4 h-4 text-muted-foreground" />
            Change password
          </button>

          <button
            onClick={handleLogout}
            className="w-full px-3 py-2 flex items-center gap-2 text-sm text-foreground hover:bg-muted transition text-left"
          >
            <LogOut className="w-4 h-4 text-muted-foreground" />
            Sign out
          </button>
        </div>
      )}

      <ChangePasswordDialog open={pwdOpen} onClose={() => setPwdOpen(false)} />
    </div>
  );
}