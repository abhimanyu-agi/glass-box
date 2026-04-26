"""
End-to-end CLI runner for the agent.

Usage:
  python -m agent.scripts.run_agent                    # runs the preset demo battery
  python -m agent.scripts.run_agent --interactive      # type your own questions
  python -m agent.scripts.run_agent --trace            # include verbose trace
"""

import sys
import time
from agent.graph import build_agent


def pretty_print(state: dict, show_trace: bool = False):
    print("\n" + "=" * 100)
    print(f"❓ {state['question']}")
    print("=" * 100)
    print(f"\nIntent: {state.get('intent', '—')} "
          f"(conf {state.get('intent_confidence', 0):.2f})")
    print(f"Chart:  {state.get('chart_type', 'none')}")

    sql = state.get("generated_sql", "")
    if sql:
        print(f"\nSQL:\n{sql.strip()}")

    df = state.get("query_result_df")
    if df is not None and len(df) > 0:
        print(f"\nDATA ({len(df)} rows):")
        print(df.head(10).to_string(index=False))

    print(f"\n💡 NARRATIVE:\n{state.get('narrative', '')}")

    followups = state.get("suggested_followups", [])
    if followups:
        print("\n🔎 Suggested follow-ups:")
        for q in followups:
            print(f"  - {q}")

    cost = state.get("total_cost_usd", 0.0)
    print(f"\n💰 cost: ${cost:.4f}")

    if show_trace:
        print("\nTRACE:")
        for line in state.get("trace", []):
            print(f"  {line}")


def run_one(agent, question: str, show_trace: bool = False):
    initial = {
        "question": question,
        "trace": [],
        "total_cost_usd": 0.0,
        "retry_count": 0,
    }
    t0 = time.time()
    result = agent.invoke(initial)
    elapsed = time.time() - t0
    pretty_print(result, show_trace=show_trace)
    print(f"⏱  elapsed: {elapsed:.2f}s")


DEMO_QUESTIONS = [
    "How many severe incidents happened in California in 2022?",
    "Compare California and Texas for severe accidents in 2022",
    "Monthly trend of severe incidents in Florida over 2022",
    "Top 5 weather conditions causing severe accidents",
    "Which cities had the most critical incidents last year?",
    "What's the year-over-year change in night-time incidents?",
    "What's the capital of France?",
]


def demo_battery(show_trace: bool):
    agent = build_agent()
    for q in DEMO_QUESTIONS:
        run_one(agent, q, show_trace=show_trace)


def interactive(show_trace: bool):
    agent = build_agent()
    print("\n🤖 AI Safety Analyst. Type a question, or 'quit' to exit.\n")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in ("quit", "exit", "q", ""):
            break
        try:
            run_one(agent, q, show_trace=show_trace)
        except Exception as e:
            print(f"❌ Agent crashed: {e}")


if __name__ == "__main__":
    show_trace = "--trace" in sys.argv
    if "--interactive" in sys.argv:
        interactive(show_trace)
    else:
        demo_battery(show_trace)