"""
Reads measures_catalog, dimensions_catalog, dimension_values
and populates semantic_index with OpenAI embeddings.

Idempotent — safe to re-run. It wipes and repopulates semantic_index.

Cost estimate: ~40 rows × ~100 tokens each = 4K tokens
At $0.02 / 1M tokens for text-embedding-3-small, total cost ~$0.0001.
"""

import os
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from openai import OpenAI

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536


def get_db_connection():
    """Open a Postgres connection using .env credentials."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed_batch(texts):
    """
    Embed a list of strings in ONE API call (batching = cheaper + faster).
    Returns list of 1536-dim vectors.
    """
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


# ---------------------------------------------------------------------------
# Build rich text descriptions per object type
# The more context we pack in here, the better semantic search will work.
# ---------------------------------------------------------------------------

def build_measure_text(row):
    """
    Compose a rich, natural-language description for a measure.
    This is what actually gets embedded — the quality of this text
    directly drives the quality of search results.
    """
    (name, display, description, sql_expr, source, unit, higher_better,
     synonyms, examples, preferred_chart, trend_dir, format_hint) = row

    synonyms_str = ", ".join(synonyms or [])
    examples_str = "; ".join(examples or [])

    return (
        f"MEASURE: {display} ({name}). "
        f"DESCRIPTION: {description} "
        f"UNIT: {unit}. "
        f"SYNONYMS: {synonyms_str}. "
        f"EXAMPLE QUESTIONS: {examples_str}. "
        f"PREFERRED VISUALIZATION: {preferred_chart}."
    )


def build_dimension_text(row):
    """Description for a dimension (e.g., state, weather_condition)."""
    name, display, description, source_col, source_view, synonyms, samples = row
    synonyms_str = ", ".join(synonyms or [])
    samples_str = ", ".join(samples or [])
    return (
        f"DIMENSION: {display} ({name}). "
        f"DESCRIPTION: {description} "
        f"SYNONYMS: {synonyms_str}. "
        f"EXAMPLE VALUES: {samples_str}."
    )


def build_dim_value_text(row):
    """Description for a dimension VALUE (e.g., 'California' -> CA)."""
    _, dim_name, canonical, display, aliases = row
    aliases_str = ", ".join(aliases or [])
    return (
        f"VALUE: {display} (code: {canonical}). "
        f"BELONGS TO DIMENSION: {dim_name}. "
        f"ALIASES: {aliases_str}."
    )


# ---------------------------------------------------------------------------
# Main ingestion logic
# ---------------------------------------------------------------------------

def ingest():
    conn = get_db_connection()
    conn.autocommit = False

    records_to_insert = []

    with conn.cursor() as cur:
        # ---- Measures ----
        print("Reading measures_catalog...")
        cur.execute("""
            SELECT measure_name, display_name, description, sql_expression,
                   source_view, unit, higher_is_better, synonyms,
                   example_questions, preferred_chart, trend_direction, format_hint
            FROM measures_catalog
            ORDER BY measure_name
        """)
        for row in cur.fetchall():
            text = build_measure_text(row)
            metadata = {
                "sql_expression": row[3],
                "source_view": row[4],
                "unit": row[5],
                "higher_is_better": row[6],
                "preferred_chart": row[9],
                "format_hint": row[11],
            }
            records_to_insert.append(
                ("measure", row[0], row[1], row[2], text, metadata)
            )

        # ---- Dimensions ----
        print("Reading dimensions_catalog...")
        cur.execute("""
            SELECT dimension_name, display_name, description,
                   source_column, source_view, synonyms, sample_values
            FROM dimensions_catalog
            ORDER BY dimension_name
        """)
        for row in cur.fetchall():
            text = build_dimension_text(row)
            metadata = {
                "source_column": row[3],
                "source_view": row[4],
                "sample_values": row[6],
            }
            records_to_insert.append(
                ("dimension", row[0], row[1], row[2], text, metadata)
            )

        # ---- Dimension values ----
        print("Reading dimension_values...")
        cur.execute("""
            SELECT id, dimension_name, canonical_value, display_name, aliases
            FROM dimension_values
            ORDER BY dimension_name, canonical_value
        """)
        for row in cur.fetchall():
            text = build_dim_value_text(row)
            metadata = {
                "dimension_name": row[1],
                "canonical_value": row[2],
            }
            # Unique object_name to avoid collisions
            object_name = f"{row[1]}:{row[2]}"
            records_to_insert.append(
                ("dim_value", object_name, row[3],
                 f"Alias mapping for {row[3]}", text, metadata)
            )

    print(f"\nTotal records to embed: {len(records_to_insert)}")

    # ---- Batch embed (one API call, massively cheaper) ----
    texts_to_embed = [rec[4] for rec in records_to_insert]
    print(f"Calling OpenAI embeddings API (1 batch, {len(texts_to_embed)} items)...")
    embeddings = embed_batch(texts_to_embed)
    print(f"  Received {len(embeddings)} embeddings of dim {len(embeddings[0])}")

    # ---- Write to DB ----
    with conn.cursor() as cur:
        print("Clearing semantic_index...")
        cur.execute("TRUNCATE TABLE semantic_index RESTART IDENTITY;")

        print("Inserting embeddings...")
        insert_rows = []
        for (obj_type, obj_name, display, description, text, metadata), emb in zip(
            records_to_insert, embeddings
        ):
            # pgvector accepts vectors as strings in bracket form: "[0.1, 0.2, ...]"
            emb_str = "[" + ",".join(f"{x:.6f}" for x in emb) + "]"
            insert_rows.append((
                obj_type, obj_name, display, description,
                text, emb_str, json.dumps(metadata)
            ))

        execute_values(
            cur,
            """
            INSERT INTO semantic_index
                (object_type, object_name, display_name, description,
                 embedding_text, embedding, metadata)
            VALUES %s
            """,
            insert_rows,
            template="(%s, %s, %s, %s, %s, %s::vector, %s::jsonb)",
        )

    conn.commit()
    conn.close()
    print(f"\n✅ Ingested {len(records_to_insert)} embeddings into semantic_index")


if __name__ == "__main__":
    ingest()