import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { YearProvider } from "@/contexts/YearContext";
import { RailProvider } from "@/contexts/RailContext";
import AppLayout from "@/components/AppLayout";
import ProtectedRoute from "@/components/ProtectedRoute";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import ReportsPage from "@/pages/ReportsPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 min
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Temporary placeholder — replaced in Step 3
function DashboardPlaceholder() {
  return (
    <div className="p-8 space-y-4">
      <p className="text-sm text-muted-foreground">
        Dashboard content goes here in Step 4.
      </p>
      <div className="grid grid-cols-4 gap-4">
        {["Total", "Severe", "Rate", "YoY"].map((label) => (
          <div
            key={label}
            className="bg-card border border-border rounded-lg p-5"
          >
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              {label}
            </p>
            <p className="text-3xl font-semibold tracking-tight text-foreground mt-2">
              —
            </p>
          </div>
        ))}
      </div>
      <div className="bg-card border border-border rounded-lg p-6 h-64 flex items-center justify-center">
        <p className="text-sm text-muted-foreground">
          Trend chart placeholder
        </p>
      </div>
    </div>
  );
}

function ReportsPlaceholder() {
  return (
    <div className="max-w-3xl mx-auto px-8 py-12 space-y-4">
      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">
        Q1 2023 · Editorial
      </p>
      <h2 className="text-3xl font-semibold tracking-tight text-foreground leading-tight">
        Reports page placeholder.
      </h2>
      <p className="text-base text-muted-foreground leading-relaxed">
        This is where the Direction 3 narrative layout lives. Built in Step 5.
      </p>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <YearProvider>
            <RailProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                <Route element={<ProtectedRoute />}>
                  <Route element={<AppLayout />}>
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/reports" element={<ReportsPage />} />
                  </Route>
                </Route>

                <Route
                  path="/"
                  element={<Navigate to="/dashboard" replace />}
                />
                <Route
                  path="*"
                  element={<Navigate to="/dashboard" replace />}
                />
              </Routes>
            </BrowserRouter>
            </RailProvider>
          </YearProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;