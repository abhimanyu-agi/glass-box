"""
Node 1: Classify the user's intent and route the graph.

Cheap model (gpt-4o-mini) + structured JSON output.
"""

import json
from agent.state import AgentState
from agent.llm import chat_completion
from agent.prompts import CLASSIFIER_SYSTEM, CLASSIFIER_USER
import os


def classify_intent(state: AgentState) -> AgentState:
    question = state["question"]
    history = state.get("conversation_history", []) or []
    trace = state.get("trace", [])
    total_cost = state.get("total_cost_usd", 0.0)

    trace.append(f"[classify] input: {question!r} (history turns: {len(history)})")

    model = os.getenv("MODEL_CLASSIFIER", "gpt-4o-mini")

    # Build history block — last 4 turns max to keep tokens low
    history_block = ""
    if history:
        recent = history[-4:]
        lines = []
        for turn in recent:
            role = turn.get("role", "user").upper()
            content = (turn.get("content") or "")[:300]
            lines.append(f"{role}: {content}")
        history_block = "CONVERSATION HISTORY (most recent last):\n" + "\n".join(lines) + "\n"

    content, usage = chat_completion(
        model=model,
        messages=[
            {"role": "system", "content": CLASSIFIER_SYSTEM},
            {"role": "user", "content": CLASSIFIER_USER.format(
                history_block=history_block,
                question=question,
            )},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    try:
        parsed = json.loads(content)
        intent = parsed.get("intent", "ambiguous")
        confidence = float(parsed.get("confidence", 0.0))
        reasoning = parsed.get("reasoning", "")
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        trace.append(f"[classify] PARSE_ERROR: {e}, raw={content!r}")
        intent = "ambiguous"
        confidence = 0.0
        reasoning = f"Classifier output unparseable: {e}"

    valid = {"metric_lookup", "comparison", "trend", "out_of_scope", "ambiguous"}
    if intent not in valid:
        trace.append(f"[classify] INVALID_INTENT: {intent!r} → coerced to ambiguous")
        intent = "ambiguous"

    trace.append(
        f"[classify] intent={intent} conf={confidence:.2f} cost=${usage['cost_usd']:.6f}"
    )

    return {
        "intent": intent,
        "intent_confidence": confidence,
        "classifier_reasoning": reasoning,
        "total_cost_usd": total_cost + usage["cost_usd"],
        "trace": trace,
    }