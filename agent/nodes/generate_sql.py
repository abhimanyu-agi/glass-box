"""
Node 3: Generate SQL from the user's question + retrieved metadata.

Uses gpt-4o with structured JSON output. This is the most expensive node
(~$0.005 per call) so we do NOT retry here — the repair loop (Node 5)
handles SQL errors.
"""

import json
import os
from agent.state import AgentState
from agent.llm import chat_completion
from agent.prompts import SQL_GEN_SYSTEM, SQL_GEN_USER
from agent.schema_context import VIEWS_SCHEMA, retrieved_items_context


def generate_sql(state: AgentState) -> AgentState:
    question = state["question"]
    items = state.get("retrieved_items", [])
    trace = state.get("trace", [])
    total_cost = state.get("total_cost_usd", 0.0)

    trace.append(f"[generate_sql] starting with {len(items)} retrieved items")

    model = os.getenv("MODEL_SQL_GEN", "gpt-4o")

    history = state.get("conversation_history", []) or []
    history_block = ""
    if history:
        recent = history[-4:]
        lines = []
        for turn in recent:
            role = turn.get("role", "user").upper()
            content = (turn.get("content") or "")[:300]
            lines.append(f"{role}: {content}")
        history_block = "RECENT CONVERSATION (most recent last):\n" + "\n".join(lines) + "\n"

    user_msg = SQL_GEN_USER.format(
        schema=VIEWS_SCHEMA,
        retrieved_context=retrieved_items_context(items),
        history_block=history_block,
        question=question,
    )

    content, usage = chat_completion(
        model=model,
        messages=[
            {"role": "system", "content": SQL_GEN_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    # Parse the structured response
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        trace.append(f"[generate_sql] PARSE_ERROR: {e}")
        return {
            "generated_sql": "",
            "chart_type": "table",
            "sql_explanation": f"SQL generator output unparseable: {e}",
            "total_cost_usd": total_cost + usage["cost_usd"],
            "trace": trace,
        }

    is_answerable = parsed.get("is_answerable", True)

    if not is_answerable:
        clarification = parsed.get("clarification_needed", "")
        trace.append(f"[generate_sql] not answerable: {clarification}")
        return {
            "generated_sql": "",
            "chart_type": "table",
            "sql_explanation": f"Question not answerable from schema. {clarification}",
            "total_cost_usd": total_cost + usage["cost_usd"],
            "trace": trace,
        }

    sql = (parsed.get("sql") or "").strip()
    chart_type = parsed.get("chart_type", "table")
    explanation = parsed.get("explanation", "")
    assumptions = parsed.get("assumptions", []) or []

    # Light validation — catch obvious mistakes early
    validation_errors = _validate_sql(sql)
    if validation_errors:
        trace.append(f"[generate_sql] VALIDATION: {'; '.join(validation_errors)}")
        # We still pass the SQL through; the executor/repair will handle it.

    trace.append(f"[generate_sql] chart={chart_type} cost=${usage['cost_usd']:.6f}")
    trace.append(f"[generate_sql] sql preview: {sql[:160]}...")

    new_state = {
        "generated_sql": sql,
        "chart_type": chart_type,
        "sql_explanation": explanation,
        "total_cost_usd": total_cost + usage["cost_usd"],
        "trace": trace,
    }
    if assumptions:
        new_state["trace"].append(f"[generate_sql] assumptions: {assumptions}")
    return new_state


def _validate_sql(sql: str) -> list[str]:
    """
    Fast sanity checks. NOT a parser — just catches the worst mistakes
    without running the query.
    """
    errors: list[str] = []
    s = sql.upper()

    if not s.strip():
        errors.append("empty SQL")
        return errors

    if not (s.startswith("SELECT") or s.startswith("WITH")):
        errors.append("SQL must start with SELECT or WITH")

    # Deny statement injection (defence in depth — exec role is already limited)
    for bad_kw in ("DROP ", "DELETE ", "UPDATE ", "INSERT ", "ALTER ", "TRUNCATE ", "GRANT "):
        if bad_kw in s:
            errors.append(f"disallowed keyword: {bad_kw.strip()}")

    # Valid source views
    valid_sources = ("V_SAFETY_MEASURES", "MV_INCIDENTS_WEATHER_MONTHLY",
                     "MV_INCIDENTS_CITY_MONTHLY", "MV_INCIDENTS_MONTHLY")
    if not any(v in s for v in valid_sources):
        errors.append("SQL does not reference any known view")

    return errors