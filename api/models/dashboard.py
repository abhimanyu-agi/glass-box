"""Pydantic response schemas for dashboard endpoints."""

from datetime import date
from pydantic import BaseModel


class KPISummary(BaseModel):
    total_incidents:  int
    severe_incidents: int
    severe_rate_pct:  float
    yoy_change_pct:   float
    year:             int


class TrendPoint(BaseModel):
    incident_month:   date
    total_incidents:  int
    severe_incidents: int


class StateRow(BaseModel):
    state:            str
    total_incidents:  int
    severe_incidents: int
    severe_rate_pct:  float


class WeatherRow(BaseModel):
    weather_condition: str
    total_incidents:   int
    severe_incidents:  int
    severe_rate_pct:   float


class CityRow(BaseModel):
    state:               str
    city:                str
    total_incidents:     int
    severe_incidents:    int
    critical_incidents:  int


class AvailableYears(BaseModel):
    years: list[int]