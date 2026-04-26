"""
Assemble the LangGraph.

The graph has a linear happy path with two conditional branches:
  classify -> retrieve -> generate_sql -> execute_sql -> narrate -> END
                                               ^             |
                                               |             v
                                           repair_sql  (or) out_of_scope
"""

from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes.classify import classify_intent
from agent.nodes.retrieve import retrieve_metadata
from agent.nodes.generate_sql import generate_sql
from agent.nodes.execute_sql import execute_sql
from agent.nodes.repair_sql import repair_sql
from agent.nodes.narrate import narrate
from agent.routing import route_after_classify, route_after_execute


def out_of_scope_node(state: AgentState) -> AgentState:
    """
    Short-circuit node for out-of-scope or ambiguous questions.
    Skips SQL entirely — just writes a narrative and follow-up suggestions.
    """
    trace = state.get("trace", [])
    intent = state.get("intent", "")
    reasoning = state.get("classifier_reasoning", "")

    if intent == "out_of_scope":
        narrative = (
            "This question is outside the scope of the US road-safety data I work with. "
            "I can answer questions about US road incidents, weather impact on safety, "
            "severity breakdowns, and time-based trends from 2016 to early 2023."
        )
    else:
        narrative = (
            "I need more specifics to answer that. "
            f"({reasoning})"
        )

    trace.append(f"[out_of_scope] intent={intent}")

    return {
        "narrative": narrative,
        "suggested_followups": [
            "How many severe incidents happened in California last year?",
            "Which weather conditions cause the most severe accidents?",
            "Compare CA and TX for night-time incidents in 2022",
        ],
        "chart_type": "none",
        "trace": trace,
    }


def greeting_node(state: AgentState) -> AgentState:
    """
    Short-circuit node for greetings and pleasantries.
    Skips SQL entirely — returns a warm response and starter suggestions.
    """
    trace = state.get("trace", [])
    trace.append("[greeting] short-circuit response")

    return {
        "narrative": (
            "Happy to help. I work with US road-safety data from 2016 to early 2023 — "
            "incidents, severity, weather impact, and trends by state, city, and time. "
            "What would you like to explore?"
        ),
        "suggested_followups": [
            "How many severe incidents happened in California last year?",
            "Which weather conditions cause the most severe accidents?",
            "Show me the monthly trend of severe incidents",
        ],
        "chart_type": "none",
        "trace": trace,
    }


def build_agent():
    """
    Compile the LangGraph. Returns a callable `graph.invoke(initial_state)`.
    """
    builder = StateGraph(AgentState)

    # Register nodes
    builder.add_node("classify", classify_intent)
    builder.add_node("retrieve", retrieve_metadata)
    builder.add_node("generate_sql", generate_sql)
    builder.add_node("execute_sql", execute_sql)
    builder.add_node("repair_sql", repair_sql)
    builder.add_node("narrate", narrate)
    builder.add_node("out_of_scope", out_of_scope_node)
    builder.add_node("greeting", greeting_node)

    # Entry
    builder.set_entry_point("classify")

    # After classify: answer path or short-circuit
    builder.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "retrieve": "retrieve",
            "out_of_scope": "out_of_scope",
            "greeting": "greeting",
        },
    )

    # Linear middle section
    builder.add_edge("retrieve", "generate_sql")
    builder.add_edge("generate_sql", "execute_sql")

    # After execute: narrate, repair, or give up
    builder.add_conditional_edges(
        "execute_sql",
        route_after_execute,
        {"narrate": "narrate", "repair": "repair_sql"},
    )

    # Repair loops back to execute
    builder.add_edge("repair_sql", "execute_sql")

    # Terminals
    builder.add_edge("narrate", END)
    builder.add_edge("out_of_scope", END)
    builder.add_edge("greeting", END)

    return builder.compile()