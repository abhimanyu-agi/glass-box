"""Smoke-test every dashboard data function."""

from ui.data import (
    kpi_summary,
    monthly_trend,
    top_states,
    weather_impact,
    city_hotspots,
    available_years,
)

print("--- KPI summary for 2022 ---")
print(kpi_summary(2022))

print("\n--- Available years ---")
print(available_years())

print("\n--- Monthly trend (24 months) ---")
df = monthly_trend(24)
print(f"Rows: {len(df)}")
print(df.head())

print("\n--- Top 10 states 2022 ---")
df = top_states(2022)
print(df)

print("\n--- Weather impact 2022 ---")
df = weather_impact(2022)
print(df)

print("\n--- City hotspots 2022 (top 5) ---")
df = city_hotspots(2022, top_n=5)
print(df)