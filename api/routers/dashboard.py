"""/dashboard/* — KPIs, trend, states, weather, hotspots, years."""

import asyncio

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_current_user
from api.models.dashboard import (
    AvailableYears,
    CityRow,
    KPISummary,
    StateRow,
    TrendPoint,
    WeatherRow,
)
from api.models.user import UserPublic
from api.services import dashboard_service


router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(get_current_user)],   # protect all endpoints with JWT
)


@router.get("/kpis", response_model=KPISummary)
async def get_kpis(
    year: int = Query(2022, ge=2016, le=2023, description="Fiscal year to summarize"),
):
    return await asyncio.to_thread(dashboard_service.kpi_summary, year)


@router.get("/trend", response_model=list[TrendPoint])
async def get_trend(
    months: int = Query(24, ge=1, le=96, description="Lookback window in months"),
):
    return await asyncio.to_thread(dashboard_service.monthly_trend, months)


@router.get("/states", response_model=list[StateRow])
async def get_top_states(
    year:  int = Query(2022, ge=2016, le=2023),
    top_n: int = Query(10,   ge=1,    le=50),
):
    return await asyncio.to_thread(dashboard_service.top_states, year, top_n)


@router.get("/weather", response_model=list[WeatherRow])
async def get_weather_impact(
    year:          int = Query(2022, ge=2016, le=2023),
    min_incidents: int = Query(500,  ge=0),
    top_n:         int = Query(10,   ge=1,    le=50),
):
    return await asyncio.to_thread(
        dashboard_service.weather_impact, year, min_incidents, top_n
    )


@router.get("/hotspots", response_model=list[CityRow])
async def get_city_hotspots(
    year:  int = Query(2022, ge=2016, le=2023),
    top_n: int = Query(15,   ge=1,    le=100),
):
    return await asyncio.to_thread(dashboard_service.city_hotspots, year, top_n)


@router.get("/years", response_model=AvailableYears)
async def get_available_years(
    current_user: UserPublic = Depends(get_current_user),
):
    years = await asyncio.to_thread(dashboard_service.available_years)
    return {"years": years}