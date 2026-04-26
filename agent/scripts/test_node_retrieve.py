"""Test Node 2 (semantic retriever) in isolation."""

from agent.nodes.retrieve import retrieve_metadata

tests = [
    "Severe accidents in California in March 2022",
    "Compare CA and TX for severity",
    "Weather-related incidents trend",
    "After-dark crashes",
    "Top cities for severe accidents",
]

for q in tests:
    state = {"question": q, "trace": []}
    result = retrieve_metadata(state)
    print(f"\nQ: {q}")
    print(f"   best_distance: {result['retrieval_best_distance']:.4f}")
    print(f"   retrieved ({len(result['retrieved_items'])}):")
    for it in result["retrieved_items"]:
        print(
            f"     - {it['object_type']:10s} {it['object_name']:30s}"
            f" d={it['distance']:.3f} ({it['confidence']})"
        )