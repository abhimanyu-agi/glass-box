"""
Node 4: Execute the generated SQL against Postgres.

Responsibilities:
- Run the SQL read-only against finance_poc
- Catch errors without letting them bubble up
- Cap execution time so a runaway query can't hang the agent
- Return a pandas DataFrame in state for downstream nodes

This node does NOT decide whether to repair. That's a graph-level decision
made by the conditional edge after this node.
"""

import pandas as pd
from agent.state import AgentState
from agent.db import get_conn


# Safety cap — abort any query that runs longer than this.
# Our MVs are small; anything slower than this means something is wrong.
STATEMENT_TIMEOUT_MS = 20_000   # 20 seconds


def execute_sql(state: AgentState) -> AgentState:
    sql = state.get("generated_sql", "").strip()
    trace = state.get("trace", [])
    retry_count = state.get("retry_count", 0)

    # Empty SQL means the generator declared the question unanswerable.
    # Just pass through — the narrator will handle the "I can't answer" path.
    if not sql:
        trace.append("[execute_sql] skipped — SQL is empty (is_answerable=false)")
        return {
            "query_result_df": None,
            "query_result_rows": 0,
            "execute_error": None,
            "trace": trace,
        }

    trace.append(f"[execute_sql] attempt {retry_count + 1}")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SET statement_timeout = {STATEMENT_TIMEOUT_MS}")
            df = pd.read_sql(sql, conn)

        rows = len(df)
        trace.append(f"[execute_sql] success — {rows} rows returned")

        return {
            "query_result_df": df,
            "query_result_rows": rows,
            "execute_error": None,
            "trace": trace,
        }

    except Exception as e:
        # Postgres errors come through as psycopg2 exceptions, but we catch
        # Exception to also cover pandas parsing edge cases.
        err_str = str(e).strip()
        # Trim verbose Postgres tracebacks for the repair prompt
        short_err = err_str.split("\n")[0][:300]
        trace.append(f"[execute_sql] ERROR: {short_err}")

        return {
            "query_result_df": None,
            "query_result_rows": 0,
            "execute_error": err_str,
            "trace": trace,
        }