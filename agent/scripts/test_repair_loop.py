"""
Test the execute → repair → execute loop manually.
We deliberately inject a broken SQL, then verify the repair path.
"""

from agent.nodes.retrieve import retrieve_metadata
from agent.nodes.execute_sql import execute_sql
from agent.nodes.repair_sql import repair_sql


question = "How many severe incidents in California in 2022?"

# Seed state with retrieved items (so the repair has context)
state = {"question": question, "trace": [], "total_cost_usd": 0.0}
state.update(retrieve_metadata(state))

# Inject deliberately-broken SQL (hallucinated column)
state["generated_sql"] = "SELECT banana_count FROM v_safety_measures"
state["retry_count"] = 0

print("=" * 90)
print("ATTEMPT 1: execute the bad SQL")
print("=" * 90)
state.update(execute_sql(state))
print(f"error:  {state['execute_error'][:150] if state['execute_error'] else None}")
print(f"rows:   {state['query_result_rows']}")

# Error is present, run the repair node
if state.get("execute_error"):
    print("\n" + "=" * 90)
    print("REPAIR attempt")
    print("=" * 90)
    state.update(repair_sql(state))
    print(f"new sql:\n{state['generated_sql']}")

    # Re-run execute with the repaired SQL
    print("\n" + "=" * 90)
    print("ATTEMPT 2: execute the repaired SQL")
    print("=" * 90)
    state.update(execute_sql(state))
    print(f"error:  {state['execute_error']}")
    print(f"rows:   {state['query_result_rows']}")
    if state["query_result_df"] is not None:
        print(state["query_result_df"])

print("\nFINAL TRACE:")
for line in state["trace"]:
    print(f"  {line}")

print(f"\nTotal cost: ${state['total_cost_usd']:.6f}")