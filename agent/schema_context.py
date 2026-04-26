"""
Schema context builder — produces the schema-awareness section of the SQL-gen prompt.

Kept in its own module so we can tweak it without touching prompts or nodes.
"""

from agent.db import get_conn


# Static schema documentation. We prefer this to fully-dynamic introspection
# because it lets us annotate things (e.g., "always filter state IS NOT NULL").
VIEWS_SCHEMA = """
PRIMARY VIEW: v_safety_measures
  Grain: one row per (incident_month, state)
  Time column: incident_month (DATE, first day of the month)
  Additional time columns: incident_year (INT), month_num (INT), quarter_num (INT)
  Dimension columns: state (TEXT, 2-letter US code, e.g. 'CA')
  Measure columns (all numeric):
    mtd_total, mtd_severe, mtd_critical, mtd_night,
    mtd_weather_related, mtd_signal_involved, mtd_junction,
    mtd_avg_distance, mtd_avg_duration,
    mtd_severe_rate_pct, mtd_weather_rate_pct,
    ytd_total, ytd_severe,
    ltm_total, ltm_severe,
    prev_month_total, prev_year_month_total,
    mom_change_pct, yoy_change_pct

SUPPORTING VIEW: mv_incidents_weather_monthly
  Grain: one row per (incident_month, state, weather_condition)
  Columns: incident_month, incident_year, state, weather_condition,
           total_incidents, severe_incidents, avg_distance_mi,
           avg_visibility_mi, avg_precipitation_in

SUPPORTING VIEW: mv_incidents_city_monthly
  Grain: one row per (incident_month, state, city)
  Columns: incident_month, incident_year, state, city,
           total_incidents, severe_incidents, critical_incidents, avg_distance_mi

SUPPORTING VIEW: mv_incidents_monthly
  Grain: one row per (incident_month, state, county, severity, sunrise_sunset)
  Use this view only when the question mentions severity level OR day/night breakdown.
  Columns: incident_month, incident_year, month_num, quarter_num, state, county,
           severity, sunrise_sunset,
           total_incidents, severe_incidents, critical_incidents, night_incidents,
           signal_involved_incidents, junction_incidents, weather_related_incidents,
           avg_distance_mi, avg_duration_min,
           avg_temperature_f, avg_visibility_mi, avg_wind_speed_mph

DATA RANGE: incidents exist from 2016-01 to 2023-03 inclusive.
TODAY (for relative time expressions): assume 2023-03-31.
"""


def retrieved_items_context(items: list) -> str:
    """
    Format retrieved items as a compact, LLM-readable context block.
    Emphasises strong and likely matches; includes metadata hints.
    """
    if not items:
        return "(no retrieved items — question may be out of scope)"

    lines = []
    for it in items:
        tag = it["confidence"].upper()
        line = f"- [{tag}] {it['object_type']}: {it['object_name']}"
        line += f"  ({it['display_name']})"
        line += f"  — {it['description']}"

        meta = it.get("metadata") or {}
        hints = []
        if "sql_expression" in meta:
            hints.append(f"sql: {meta['sql_expression']}")
        if "source_view" in meta:
            hints.append(f"view: {meta['source_view']}")
        if "canonical_value" in meta:
            hints.append(f"value: {meta['canonical_value']}")
        if "source_column" in meta:
            hints.append(f"column: {meta['source_column']}")
        if hints:
            line += f"   [{'; '.join(hints)}]"

        lines.append(line)

    return "\n".join(lines)