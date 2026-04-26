"""
Node 5: Repair broken SQL based on the Postgres error message.

Called only when execute_sql returned an error AND retry_count < MAX_SQL_REPAIRS.
Re-runs generation with error context, returns corrected SQL.
After this, the graph re-executes; success -> narrate, fail again -> repair again.
"""

import json
import os
from agent.state import AgentState
from agent.llm import chat_completion
from agent.prompts import SQL_REPAIR_SYSTEM, SQL_REPAIR_USER
from agent.schema_context import VIEWS_SCHEMA, retrieved_items_context


def repair_sql(state: AgentState) -> AgentState:
    question = state["question"]
    broken_sql = state.get("generated_sql", "")
    error = state.get("execute_error", "")
    items = state.get("retrieved_items", [])
    trace = state.get("trace", [])
    retry_count = state.get("retry_count", 0)
    total_cost = state.get("total_cost_usd", 0.0)

    attempt = retry_count + 1
    trace.append(f"[repair_sql] repair attempt {attempt}")

    model = os.getenv("MODEL_SQL_GEN", "gpt-4o")

    user_msg = SQL_REPAIR_USER.format(
        schema=VIEWS_SCHEMA,
        retrieved_context=retrieved_items_context(items),
        question=question,
        attempt=attempt,
        broken_sql=broken_sql,
        error=error,
    )

    content, usage = chat_completion(
        model=model,
        messages=[
            {"role": "system", "content": SQL_REPAIR_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    try:
        parsed = json.loads(content)
        new_sql = (parsed.get("sql") or "").strip()
        fix_explanation = parsed.get("fix_explanation", "")
    except json.JSONDecodeError as e:
        trace.append(f"[repair_sql] PARSE_ERROR: {e}")
        new_sql = ""
        fix_explanation = f"repair output unparseable: {e}"

    trace.append(f"[repair_sql] fix: {fix_explanation}")
    trace.append(f"[repair_sql] cost=${usage['cost_usd']:.6f}")
    if new_sql:
        trace.append(f"[repair_sql] new sql preview: {new_sql[:160]}...")

    return {
        "generated_sql": new_sql,
        "retry_count": attempt,
        # Clear the old error so the next execute attempt starts clean
        "execute_error": None,
        "total_cost_usd": total_cost + usage["cost_usd"],
        "trace": trace,
    }