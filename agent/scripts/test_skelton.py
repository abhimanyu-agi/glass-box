"""Smoke test: verify agent skeleton modules import and basic calls work."""

from agent.db import get_conn
from agent.llm import chat_completion, embed
from agent.state import AgentState


# DB connection
print("Testing DB...")
with get_conn() as c:
    with c.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM semantic_index;")
        count = cur.fetchone()[0]
print(f"  ✅ {count} rows in semantic_index")

# Embedding
print("Testing embedding...")
vec = embed("hello")
print(f"  ✅ got {len(vec)}-dim vector")

# LLM call
print("Testing chat completion...")
content, usage = chat_completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Reply with just the word OK."}],
)
print(f"  ✅ LLM replied: {content!r}  (cost ${usage['cost_usd']:.6f})")

# State
print("Testing state construction...")
s: AgentState = {"question": "test", "trace": []}
print(f"  ✅ AgentState ok: {s}")

print("\n✅ Skeleton is healthy.")