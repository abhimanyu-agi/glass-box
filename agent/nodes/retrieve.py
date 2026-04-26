"""
Node 2: Retrieve the most relevant metadata from pgvector.

This wraps the Phase 4 semantic search with graph-friendly structure.
"""

import os
from agent.state import AgentState, RetrievedItem
from agent.db import get_conn
from agent.llm import embed


def _confidence_label(distance: float) -> str:
    strong = float(os.getenv("CONFIDENCE_STRONG", "0.3"))
    ok = float(os.getenv("CONFIDENCE_OK", "0.5"))
    weak = float(os.getenv("CONFIDENCE_WEAK", "0.7"))

    if distance < strong:
        return "strong"
    elif distance < ok:
        return "likely"
    elif distance < weak:
        return "marginal"
    else:
        return "weak"


def retrieve_metadata(state: AgentState) -> AgentState:
    question = state["question"]
    trace = state.get("trace", [])
    top_k = int(os.getenv("RETRIEVAL_TOP_K", "8"))

    trace.append(f"[retrieve] top_k={top_k}")

    # Embed the question
    q_emb = embed(question)
    q_emb_str = "[" + ",".join(f"{x:.6f}" for x in q_emb) + "]"

    sql = """
        SELECT
            object_type,
            object_name,
            display_name,
            description,
            metadata,
            (embedding <=> %s::vector) AS distance
        FROM semantic_index
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """

    items: list[RetrievedItem] = []
    with get_conn(dict_cursor=True) as conn, conn.cursor() as cur:
        cur.execute(sql, (q_emb_str, q_emb_str, top_k))
        for row in cur.fetchall():
            dist = float(row["distance"])
            conf = _confidence_label(dist)
            # Drop the weakest matches — they add noise to the SQL prompt
            if conf == "weak":
                continue
            items.append({
                "object_type": row["object_type"],
                "object_name": row["object_name"],
                "display_name": row["display_name"],
                "description": row["description"],
                "distance": dist,
                "confidence": conf,
                "metadata": row["metadata"] or {},
            })

    best_distance = items[0]["distance"] if items else 999.0

    trace.append(
        f"[retrieve] kept {len(items)} items, best_distance={best_distance:.4f}"
    )
    for i, it in enumerate(items[:3]):
        trace.append(
            f"  #{i+1} {it['object_type']}:{it['object_name']} "
            f"(d={it['distance']:.3f}, {it['confidence']})"
        )

    return {
        "retrieved_items": items,
        "retrieval_best_distance": best_distance,
        "trace": trace,
    }