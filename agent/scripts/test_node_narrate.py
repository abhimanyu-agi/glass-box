"""Test Node 6 (narrator) with various query result shapes."""

import pandas as pd
from agent.nodes.narrate import narrate


# --- Test 1: single scalar (KPI card case) ---
state_kpi = {
    "question": "How many severe incidents in California in 2022?",
    "sql_explanation": "Count of severe incidents in CA for 2022.",
    "chart_type": "kpi_card",
    "query_result_df": pd.DataFrame({"severe_incidents": [15503]}),
    "trace": [],
    "total_cost_usd": 0.0,
}
r = narrate(state_kpi)
print("=" * 80)
print("TEST 1 — KPI scalar")
print("=" * 80)
print("Narrative:")
print(r["narrative"])
print("\nFollow-ups:")
for q in r["suggested_followups"]:
    print(f"  - {q}")
print(f"\nChart: {r['chart_type']}")


# --- Test 2: top-N ranking ---
state_bar = {
    "question": "Top 5 states by severe incidents in 2022",
    "sql_explanation": "Top 5 states by severe incidents in 2022.",
    "chart_type": "bar",
    "query_result_df": pd.DataFrame([
        {"state": "CA", "severe_incidents": 15503},
        {"state": "TX", "severe_incidents": 10129},
        {"state": "VA", "severe_incidents":  9682},
        {"state": "FL", "severe_incidents":  7194},
        {"state": "PA", "severe_incidents":  7034},
    ]),
    "trace": [],
    "total_cost_usd": 0.0,
}
r = narrate(state_bar)
print("\n" + "=" * 80)
print("TEST 2 — Bar ranking")
print("=" * 80)
print("Narrative:")
print(r["narrative"])
print("\nFollow-ups:")
for q in r["suggested_followups"]:
    print(f"  - {q}")


# --- Test 3: time series (line chart) ---
state_line = {
    "question": "Monthly trend of severe incidents in California in 2022",
    "sql_explanation": "Monthly severe incidents for CA in 2022.",
    "chart_type": "line",
    "query_result_df": pd.DataFrame([
        {"incident_month": "2022-01-01", "severe_incidents": 1100},
        {"incident_month": "2022-02-01", "severe_incidents": 1050},
        {"incident_month": "2022-03-01", "severe_incidents": 1350},
        {"incident_month": "2022-04-01", "severe_incidents": 1200},
        {"incident_month": "2022-05-01", "severe_incidents": 1480},
        {"incident_month": "2022-06-01", "severe_incidents": 1520},
        {"incident_month": "2022-07-01", "severe_incidents": 1620},
        {"incident_month": "2022-08-01", "severe_incidents": 1580},
        {"incident_month": "2022-09-01", "severe_incidents": 1410},
        {"incident_month": "2022-10-01", "severe_incidents": 1350},
        {"incident_month": "2022-11-01", "severe_incidents": 1290},
        {"incident_month": "2022-12-01", "severe_incidents": 1550},
    ]),
    "trace": [],
    "total_cost_usd": 0.0,
}
r = narrate(state_line)
print("\n" + "=" * 80)
print("TEST 3 — Time series")
print("=" * 80)
print("Narrative:")
print(r["narrative"])
print("\nFollow-ups:")
for q in r["suggested_followups"]:
    print(f"  - {q}")


# --- Test 4: empty result ---
state_empty = {
    "question": "Severe incidents in Antarctica in 2022",
    "sql_explanation": "Count of severe incidents in Antarctica.",
    "chart_type": "kpi_card",
    "query_result_df": pd.DataFrame(columns=["severe_incidents"]),
    "trace": [],
    "total_cost_usd": 0.0,
}
r = narrate(state_empty)
print("\n" + "=" * 80)
print("TEST 4 — Empty result")
print("=" * 80)
print(r["narrative"])