import { Outlet } from "react-router-dom";
import NavRail from "./NavRail";
import AppHeader from "./AppHeader";

export default function AppLayout() {
  return (
    <div className="flex min-h-screen bg-muted/30">
      <NavRail />
      <div className="flex-1 flex flex-col min-w-0">
        <AppHeader />
        <main className="flex-1 overflow-hidden">
            <Outlet />
        </main>
      </div>
    </div>
  );
}