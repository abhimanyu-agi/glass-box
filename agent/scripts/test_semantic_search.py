"""
Interactive semantic search tester.

Two modes:
  python test_semantic_search.py              -> runs 10 preset exec-style questions
  python test_semantic_search.p y --interactive -> you type your own questions
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from openai import OpenAI
from tabulate import tabulate

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        cursor_factory=RealDictCursor,
    )


def embed(text: str):
    """Single-text embedding."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[text],
    )
    return response.data[0].embedding


def search(question: str, top_k: int = 6):
    """
    Embed the question, find top_k closest items in semantic_index
    using cosine distance (<=> operator).
    """
    q_emb = embed(question)
    q_emb_str = "[" + ",".join(f"{x:.6f}" for x in q_emb) + "]"

    sql = """
        SELECT
            object_type,
            object_name,
            display_name,
            (embedding <=> %s::vector) AS distance
        FROM semantic_index
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (q_emb_str, q_emb_str, top_k))
        return cur.fetchall()


def confidence_label(distance: float) -> str:
    """Human-readable tag for how relevant a match is."""
    if distance < 0.3:
        return "🟢 strong"
    elif distance < 0.5:
        return "🟡 likely"
    elif distance < 0.7:
        return "🟠 marginal"
    else:
        return "🔴 weak"


def print_results(question: str, results):
    print(f"\n❓ Question: {question}\n")
    rows = [
        (
            r["object_type"],
            r["object_name"],
            r["display_name"],
            f"{r['distance']:.4f}",
            confidence_label(r["distance"]),
        )
        for r in results
    ]
    print(tabulate(
        rows,
        headers=["Type", "Object", "Display", "Distance", "Confidence"],
        tablefmt="simple",
    ))


def run_demo_questions():
    """
    Preset questions that span different executive phrasings.
    Mix of: casual, terse, abbreviated, comparison, time-based.
    """
    questions = [
        # Rainy Weather
        "Rainy weather impac?",
        

        # Basic lookups
        "How many incidents happened last month?",
        "Total accidents in California",

        # Synonym handling
        "Show me bad accidents in Cali",
        "After-dark crashes in Texas",

        # Rate / derived metrics
        "What percentage of accidents are severe?",
        "How long does it take to clear incidents?",

        # Ambiguous / broad
        "Weather impact on safety",
        "Are things getting better?",

        # Comparison
        "Year over year trend",
        "How does this month compare to last month?",
    ]
    for q in questions:
        try:
            results = search(q, top_k=5)
            print_results(q, results)
        except Exception as e:
            print(f"\n❌ Error on '{q}': {e}")
        print("-" * 90)


def interactive_mode():
    print("\n🔍 Semantic search interactive mode.")
    print("   Type a question in plain English. Type 'quit' to exit.\n")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in ("quit", "exit", "q", ""):
            break
        try:
            results = search(q, top_k=8)
            print_results(q, results)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        run_demo_questions()