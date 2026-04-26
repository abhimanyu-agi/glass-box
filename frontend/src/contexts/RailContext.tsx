import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";

const STORAGE_KEY = "safety_ops_rail_open";

interface RailContextValue {
  railOpen: boolean;
  openRail:  () => void;
  closeRail: () => void;
  toggleRail: () => void;
}

const RailContext = createContext<RailContextValue | undefined>(undefined);

function getInitial(): boolean {
  // Default closed — see decision: clean dashboard on first load
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved === "true";
}

export function RailProvider({ children }: { children: ReactNode }) {
  const [railOpen, setRailOpen] = useState<boolean>(getInitial);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(railOpen));
  }, [railOpen]);

  return (
    <RailContext.Provider
      value={{
        railOpen,
        openRail:   () => setRailOpen(true),
        closeRail:  () => setRailOpen(false),
        toggleRail: () => setRailOpen((v) => !v),
      }}
    >
      {children}
    </RailContext.Provider>
  );
}

export function useRail() {
  const ctx = useContext(RailContext);
  if (!ctx) throw new Error("useRail must be used inside <RailProvider>");
  return ctx;
}