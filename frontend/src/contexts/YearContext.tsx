import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";

interface YearContextValue {
  selectedYear: number;
  setSelectedYear: (y: number) => void;
}

const YearContext = createContext<YearContextValue | undefined>(undefined);

export function YearProvider({ children }: { children: ReactNode }) {
  const [selectedYear, setSelectedYear] = useState<number>(2022);
  return (
    <YearContext.Provider value={{ selectedYear, setSelectedYear }}>
      {children}
    </YearContext.Provider>
  );
}

export function useYear() {
  const ctx = useContext(YearContext);
  if (!ctx) throw new Error("useYear must be used inside <YearProvider>");
  return ctx;
}