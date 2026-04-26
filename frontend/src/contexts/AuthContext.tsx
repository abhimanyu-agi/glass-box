import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import * as api from "@/lib/api";
import type { UserPublic } from "@/lib/types";

interface AuthContextValue {
  user: UserPublic | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  registerAndLogin: (payload: api.RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser]       = useState<UserPublic | null>(null);
  const [loading, setLoading] = useState(true);

  // On app load, if we have a token, validate it by fetching /auth/me
  useEffect(() => {
    const token = api.getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    api.fetchCurrentUser()
      .then(setUser)
      .catch(() => api.clearToken())
      .finally(() => setLoading(false));
  }, []);

async function login(username: string, password: string) {
    const result = await api.login(username, password);
    api.setToken(result.access_token);
    setUser(result.user);
  }

  async function registerAndLogin(payload: api.RegisterPayload) {
    // Create the account, then log in to get a token
    await api.register(payload);
    const result = await api.login(payload.username, payload.password);
    api.setToken(result.access_token);
    setUser(result.user);
  }

  function logout() { 
    api.clearToken();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, registerAndLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}