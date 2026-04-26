export interface UserPublic {
  id: number;
  username: string;
  email: string | null;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string | null;
  last_login: string | null;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserPublic;
}

export interface KPISummary {
  total_incidents: number;
  severe_incidents: number;
  severe_rate_pct: number;
  yoy_change_pct: number;
  year: number;
}

export interface TrendPoint {
  incident_month: string;
  total_incidents: number;
  severe_incidents: number;
}

export interface StateRow {
  state: string;
  total_incidents: number;
  severe_incidents: number;
  severe_rate_pct: number;
}

export interface WeatherRow {
  weather_condition: string;
  total_incidents: number;
  severe_incidents: number;
  severe_rate_pct: number;
}

export interface CityRow {
  state: string;
  city: string;
  total_incidents: number;
  severe_incidents: number;
  critical_incidents: number;
}