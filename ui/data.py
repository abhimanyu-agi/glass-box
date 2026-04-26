"""
Dashboard data layer.

Every Postgres query the dashboard needs, isolated here.
Results are cached so executives don't wait on repeated queries.

Cache strategy:
- ttl=600 seconds (10 min) — dashboards are refreshed frequently by execs
- If you need live data, hit the agent chat (bypasses dashboard cache)
"""

import pandas as pd
import streamlit as st
from agent.db import get_conn


# ---------------------------------------------------------------------------
# KPI cards — four big numbers for the top row
# ---------------------------------------------------------------------------

@st.cache_data(ttl=600, show_spinner=False)
def kpi_summary(year: int = 2022) -> dict:
    """
    Returns the four headline KPIs for the given year.
    Defaults to 2022 (most recent full year in the dataset).
    """
    sql = """
        SELECT
            SUM(mtd_total)::bigint                                             AS total_incidents,
            SUM(mtd_severe)::bigint                                            AS severe_incidents,
            ROUND(100.0 * SUM(mtd_severe) / NULLIF(SUM(mtd_total), 0), 2)::float AS severe_rate_pct,
            ROUND(AVG(yoy_change_pct)::numeric, 1)::float                      AS yoy_change_pct
        FROM v_safety_measures
        WHERE incident_year = %s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (year,))
            row = cur.fetchone()

    return {
        "total_incidents":  row[0] or 0,
        "severe_incidents": row[1] or 0,
        "severe_rate_pct":  row[2] or 0.0,
        "yoy_change_pct":   row[3] or 0.0,
    }


# ---------------------------------------------------------------------------
# Trend line — monthly total & severe over the last N months
# ---------------------------------------------------------------------------

@st.cache_data(ttl=600, show_spinner=False)
def monthly_trend(months: int = 24) -> pd.DataFrame:
    """
    Monthly total + severe incidents for the last N months.
    Returns a DataFrame suitable for Plotly line charts.
    """
    sql = """
        SELECT
            incident_month,
            SUM(mtd_total)::bigint   AS total_incidents,
            SUM(mtd_severe)::bigint  AS severe_incidents
        FROM v_safety_measures
        WHERE incident_month >= (DATE '2023-03-01' - (%s || ' months')::interval)
        GROUP BY incident_month
        ORDER BY incident_month
    """
    with get_conn() as conn:
        df = pd.read_sql(sql, conn, params=(months,))
    return df


# ---------------------------------------------------------------------------
# Top N states by severe incidents
# ---------------------------------------------------------------------------

@st.cache_data(ttl=600, show_spinner=False)
def top_states(year: int = 2022, top_n: int = 10) -> pd.DataFrame:
    sql = """
        SELECT
            state,
            SUM(mtd_total)::bigint   AS total_incidents,
            SUM(mtd_severe)::bigint  AS severe_incidents,
            ROUND(100.0 * SUM(mtd_severe) / NULLIF(SUM(mtd_total), 0), 2)::float AS severe_rate_pct
        FROM v_safety_measures
        WHERE incident_year = %s
          AND state IS NOT NULL
        GROUP BY state
        ORDER BY severe_incidents DESC
        LIMIT %s
    """
    with get_conn() as conn:
        df = pd.read_sql(sql, conn, params=(year, top_n))
    return df


# ---------------------------------------------------------------------------
# Weather impact — top weather conditions by severity rate
# ---------------------------------------------------------------------------

@st.cache_data(ttl=600, show_spinner=False)
def weather_impact(year: int = 2022, min_incidents: int = 500, top_n: int = 10) -> pd.DataFrame:
    sql = """
        SELECT
            weather_condition,
            SUM(total_incidents)::bigint   AS total_incidents,
            SUM(severe_incidents)::bigint  AS severe_incidents,
            ROUND(100.0 * SUM(severe_incidents) / NULLIF(SUM(total_incidents), 0), 2)::float AS severe_rate_pct
        FROM mv_incidents_weather_monthly
        WHERE incident_year = %s
          AND weather_condition IS NOT NULL
        GROUP BY weather_condition
        HAVING SUM(total_incidents) >= %s
        ORDER BY severe_rate_pct DESC
        LIMIT %s
    """
    with get_conn() as conn:
        df = pd.read_sql(sql, conn, params=(year, min_incidents, top_n))
    return df


# ---------------------------------------------------------------------------
# City hotspots — top cities by severe incidents
# ---------------------------------------------------------------------------

@st.cache_data(ttl=600, show_spinner=False)
def city_hotspots(year: int = 2022, top_n: int = 15) -> pd.DataFrame:
    sql = """
        SELECT
            state,
            city,
            SUM(total_incidents)::bigint    AS total_incidents,
            SUM(severe_incidents)::bigint   AS severe_incidents,
            SUM(critical_incidents)::bigint AS critical_incidents
        FROM mv_incidents_city_monthly
        WHERE incident_year = %s
          AND city IS NOT NULL
        GROUP BY state, city
        ORDER BY severe_incidents DESC
        LIMIT %s
    """
    with get_conn() as conn:
        df = pd.read_sql(sql, conn, params=(year, top_n))
    return df


# ---------------------------------------------------------------------------
# Available years — used to power a year selector
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def available_years() -> list[int]:
    sql = """
        SELECT DISTINCT incident_year
        FROM v_safety_measures
        WHERE incident_year IS NOT NULL
        ORDER BY incident_year DESC
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return [r[0] for r in cur.fetchall()]