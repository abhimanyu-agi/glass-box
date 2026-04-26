"""Test Node 4 (executor) with both good and bad SQL."""

from agent.nodes.execute_sql import execute_sql

# --- Test 1: good SQL ---
state_good = {
    "generated_sql": """
        SELECT state, SUM(mtd_total) AS total
        FROM v_safety_measures
        WHERE incident_year = 2022
          AND state IS NOT NULL
        GROUP BY state
        ORDER BY total DESC
        LIMIT 5
    """,
    "trace": [],
    "retry_count": 0,
}
result = execute_sql(state_good)
print("TEST 1 — Good SQL")
print(f"  rows: {result['query_result_rows']}")
print(f"  error: {result['execute_error']}")
if result["query_result_df"] is not None:
    print(result["query_result_df"])
print()

# --- Test 2: bad SQL (hallucinated column) ---
state_bad = {
    "generated_sql": "SELECT banana_count FROM v_safety_measures",
    "trace": [],
    "retry_count": 0,
}
result = execute_sql(state_bad)
print("TEST 2 — Bad SQL")
print(f"  rows: {result['query_result_rows']}")
print(f"  error: {result['execute_error']}")
print()

# --- Test 3: empty SQL ---
state_empty = {
    "generated_sql": "",
    "trace": [],
    "retry_count": 0,
}
result = execute_sql(state_empty)
print("TEST 3 — Empty SQL (is_answerable=false path)")
print(f"  rows: {result['query_result_rows']}")
print(f"  error: {result['execute_error']}")
print(f"  trace: {result['trace']}")