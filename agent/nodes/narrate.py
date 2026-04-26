"""
Node 6: Turn the query result into an executive narrative + chart config.

Input state needs:
- question
- sql_explanation
- chart_type (suggested by SQL gen)
- query_result_df (pandas DataFrame)
- execute_error (if the whole SQL pipeline gave up)

Output state:
- narrative (markdown string)
- suggested_followups (list of strings)
- chart_type (possibly refined)
- (plus usual cost/trace updates)
"""

import json
import os
import pandas as pd
from agent.state import AgentState
from agent.llm import chat_completion
from agent.prompts import NARRATOR_SYSTEM, NARRATOR_USER


MAX_PREVIEW_ROWS = 25   # cap what we send to the LLM


def narrate(state: AgentState) -> AgentState:
    question = state["question"]
    df: pd.DataFrame | None = state.get("query_result_df")
    chart_type = state.get("chart_type", "table")
    sql_explanation = state.get("sql_explanation", "")
    execute_error = state.get("execute_error")
    trace = state.get("trace", [])
    total_cost = state.get("total_cost_usd", 0.0)

    # --- Path A: we never got valid results (after all repairs) ---
    if execute_error:
        trace.append("[narrate] SQL still broken after repairs — generating apology narrative")
        narrative = (
            "I wasn't able to answer this question from the available data. "
            "The query failed after multiple attempts."
        )
        return {
            "narrative": narrative,
            "suggested_followups": [
                "Can you rephrase the question with a specific state and time range?",
                "What data sources are available?",
            ],
            "trace": trace,
        }

    # --- Path B: the SQL generator declined (is_answerable=false) ---
    if df is None and not execute_error:
        trace.append("[narrate] no result DataFrame — SQL was empty (out of scope)")
        narrative = sql_explanation or (
            "This question is outside the scope of the available safety data."
        )
        return {
            "narrative": narrative,
            "suggested_followups": [
                "How many severe incidents happened last year?",
                "Which states have the highest incident rates?",
                "What's the weather impact on accidents?",
            ],
            "trace": trace,
        }

    # --- Path C: empty result set ---
    if df is not None and len(df) == 0:
        trace.append("[narrate] 0 rows returned")
        narrative = (
            "No records match this query. The filters may be too narrow — "
            "try broadening the time range or removing one constraint."
        )
        return {
            "narrative": narrative,
            "suggested_followups": [
                "Broaden the time range to the full year",
                "Remove the state filter and see all states",
            ],
            "trace": trace,
        }

    # --- Path D: we have real data. Call the narrator LLM. ---
    total_rows = len(df)
    preview_df = df.head(MAX_PREVIEW_ROWS)

    # Build a readable text preview for the model
    data_preview = preview_df.to_string(index=False, max_rows=MAX_PREVIEW_ROWS)

    model = os.getenv("MODEL_NARRATOR", "gpt-4o-mini")

    user_msg = NARRATOR_USER.format(
        question=question,
        sql_explanation=sql_explanation,
        chart_type=chart_type,
        n_rows=len(preview_df),
        total_rows=total_rows,
        data_preview=data_preview,
    )

    content, usage = chat_completion(
        model=model,
        messages=[
            {"role": "system", "content": NARRATOR_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,   # tiny bit of warmth in the writing
    )

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        trace.append(f"[narrate] PARSE_ERROR: {e}")
        return {
            "narrative": "(narrator output was unparseable)",
            "suggested_followups": [],
            "total_cost_usd": total_cost + usage["cost_usd"],
            "trace": trace,
        }

    narrative = parsed.get("narrative", "").strip()
    followups = parsed.get("followup_questions", []) or []
    chart_config = parsed.get("chart_config", {}) or {}

    # Let narrator refine the chart_type choice (it has seen the actual data)
    new_chart_type = chart_config.get("type", chart_type)

    trace.append(f"[narrate] chart={new_chart_type} cost=${usage['cost_usd']:.6f}")
    trace.append(f"[narrate] narrative preview: {narrative[:120]}...")

    return {
        "narrative": narrative,
        "suggested_followups": followups,
        "chart_type": new_chart_type,
        "total_cost_usd": total_cost + usage["cost_usd"],
        "trace": trace,
    }