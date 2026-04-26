import axios, { AxiosError } from "axios";
import type {
  CityRow,
  KPISummary,
  StateRow,
  Token,
  TrendPoint,
  UserPublic,
  WeatherRow,
} from "./types";

interface AvailableYears {
  years: number[];
}

// Re-export types that consumers might need; keep below the import block


const TOKEN_KEY = "safety_ops_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export const apiClient = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// Attach token to every request
apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401s globally — bounce to login
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      clearToken();
      // Don't redirect if we're already on /login
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// ----------- Voice -----------

export async function transcribeAudio(blob: Blob): Promise<string> {
  const form = new FormData();
  form.append("audio", blob, "recording.webm");

  const { data } = await apiClient.post<{ text: string }>("/chat/transcribe", form, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 60000,   // Whisper can take 5-30s for longer clips
  });
  return data.text;
}

export async function speakText(text: string, voice = "nova"): Promise<Blob> {
  const response = await apiClient.post("/chat/speak",
    { text, voice },
    {
      responseType: "blob",
      timeout: 60000,
    },
  );
  return response.data as Blob;
}


// ----------- Auth -----------

export async function login(username: string, password: string): Promise<Token> {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);

  const { data } = await apiClient.post<Token>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function fetchCurrentUser(): Promise<UserPublic> {
  const { data } = await apiClient.get<UserPublic>("/auth/me");
  return data;
}


export interface RegisterPayload {
  username: string;
  email: string;
  full_name?: string;
  password: string;
}

export async function register(payload: RegisterPayload): Promise<UserPublic> {
  const { data } = await apiClient.post<UserPublic>("/auth/register", payload);
  return data;
}

export async function changePassword(
  current_password: string,
  new_password: string
): Promise<void> {
  await apiClient.post("/auth/change-password", { current_password, new_password });
}
// ----------- Dashboard -----------

export async function fetchKPIs(year: number): Promise<KPISummary> {
  const { data } = await apiClient.get<KPISummary>("/dashboard/kpis", { params: { year } });
  return data;
}

export async function fetchTrend(months = 24): Promise<TrendPoint[]> {
  const { data } = await apiClient.get<TrendPoint[]>("/dashboard/trend", { params: { months } });
  return data;
}

export async function fetchTopStates(year: number, top_n = 10): Promise<StateRow[]> {
  const { data } = await apiClient.get<StateRow[]>("/dashboard/states", { params: { year, top_n } });
  return data;
}

export async function fetchWeatherImpact(year: number, top_n = 10): Promise<WeatherRow[]> {
  const { data } = await apiClient.get<WeatherRow[]>("/dashboard/weather", { params: { year, top_n } });
  return data;
}

export async function fetchHotspots(year: number, top_n = 15): Promise<CityRow[]> {
  const { data } = await apiClient.get<CityRow[]>("/dashboard/hotspots", { params: { year, top_n } });
  return data;
}

export async function fetchAvailableYears(): Promise<number[]> {
  const { data } = await apiClient.get<AvailableYears>("/dashboard/years");
  return data.years;
}