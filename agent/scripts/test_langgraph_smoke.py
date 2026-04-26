"""Smoke test: verify LangGraph installs cleanly and can run a trivial graph."""

from typing import TypedDict
from langgraph.graph import StateGraph, END


class TrivialState(TypedDict):
    counter: int
    message: str


def increment(state: TrivialState) -> TrivialState:
    return {"counter": state["counter"] + 1, "message": "incremented"}


def should_continue(state: TrivialState) -> str:
    return "loop" if state["counter"] < 3 else "end"


builder = StateGraph(TrivialState)
builder.add_node("incrementer", increment)
builder.set_entry_point("incrementer")
builder.add_conditional_edges(
    "incrementer",
    should_continue,
    {"loop": "incrementer", "end": END},
)

graph = builder.compile()

result = graph.invoke({"counter": 0, "message": "start"})
print("Final state:", result)
assert result["counter"] == 3, "Smoke test failed"
print("✅ LangGraph is working")