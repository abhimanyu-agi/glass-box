"""
Conditional edge functions — pure functions that read state and return
the next node name (or END).

Keeping these separate from graph.py makes them trivially unit-testable.
"""

import os
from agent.state import AgentState
from langgraph.graph import END


def route_after_classify(state: AgentState) -> str:
    """
    After the classifier, decide whether to answer or short-circuit.
    """
    intent = state.get("intent", "ambiguous")
    if intent == "greeting":
        return "greeting"
    if intent == "out_of_scope":
        return "out_of_scope"
    if intent == "ambiguous" and state.get("intent_confidence", 0) < 0.5:
        return "out_of_scope"
    return "retrieve"


def route_after_execute(state: AgentState) -> str:
    """
    After SQL execution, decide: narrate the result, repair, or give up.
    """
    max_repairs = int(os.getenv("MAX_SQL_REPAIRS", "3"))
    error = state.get("execute_error")
    retry_count = state.get("retry_count", 0)

    if error and retry_count >= max_repairs:
        # Exceeded repair budget — let the narrator explain the failure
        return "narrate"

    if error:
        return "repair"

    return "narrate"