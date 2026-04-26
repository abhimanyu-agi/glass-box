"""Test Node 3 (SQL generator) against live retrieved context."""

from agent.nodes.retrieve import retrieve_metadata
from agent.nodes.generate_sql import generate_sql

tests = [
    "How many severe incidents in California in 2022?",
    "Compare CA and TX for severe accidents in 2022",
    "Monthly incident trend in Florida over the last 24 months",
    "Top 5 weather conditions causing severe accidents",
    "What's the year-over-year change in incidents?",
    "What's the capital of France?",          # should return is_answerable=false
]

for q in tests:
    print("=" * 90)
    print(f"Q: {q}")
    state = {"question": q, "trace": [], "total_cost_usd": 0.0}

    # Step 1: retrieve
    state.update(retrieve_metadata(state))

    # Step 2: generate SQL
    state.update(generate_sql(state))

    print(f"\nCHART:        {state['chart_type']}")
    print(f"EXPLANATION:  {state['sql_explanation']}")
    print(f"COST:         ${state['total_cost_usd']:.6f}")
    print(f"\nSQL:\n{state['generated_sql']}")

    print("\nTRACE:")
    for line in state["trace"]:
        print(f"  {line}")
    print()