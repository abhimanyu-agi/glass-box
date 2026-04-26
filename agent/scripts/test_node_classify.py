"""Test Node 1 (classifier) in isolation, outside of LangGraph."""

from agent.nodes.classify import classify_intent

tests = [
    "How many severe incidents in California last month?",
    "Compare CA and TX for severe accidents",
    "Incident trend over the last 12 months",
    "What's the capital of France?",
    "Is it bad?",
    "accidents during rain",
]

for q in tests:
    state = {"question": q, "trace": [], "total_cost_usd": 0.0}
    result = classify_intent(state)
    print(f"\nQ: {q}")
    print(f"   intent     : {result['intent']}")
    print(f"   confidence : {result['intent_confidence']}")
    print(f"   reasoning  : {result['classifier_reasoning']}")
    print(f"   cost       : ${result['total_cost_usd']:.6f}")