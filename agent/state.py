"""
AgentState — the single source of truth that flows through the graph.

Design principles:
- Keep it flat (no nested dicts unless unavoidable)
- Every field has a sensible default
- Optional fields are explicitly Optional[...]
- All mutations happen by returning new dicts from nodes
"""

from typing import TypedDict, List, Optional, Literal, Any
import pandas as pd


# Intent categories the classifier can produce
Intent = Literal[
    "metric_lookup",      # "how many X in Y?"
    "comparison",         # "X vs Y" or "compare A and B"
    "trend",              # time-series-shaped questions
    "out_of_scope",       # not about our domain
    "ambiguous",          # could match multiple meanings
]


class RetrievedItem(TypedDict):
    """One row from semantic_index after retrieval."""
    object_type: str          # 'measure' | 'dimension' | 'dim_value'
    object_name: str
    display_name: str
    description: str
    distance: float
    confidence: str           # 'strong' | 'likely' | 'marginal' | 'weak'
    metadata: dict            # the JSONB column unpacked


class AgentState(TypedDict, total=False):
    # ---- INPUT ----
    question: str
    conversation_history: List[dict]
    # ---- NODE 1: CLASSIFY ----
    intent: Intent
    intent_confidence: float
    classifier_reasoning: str

    # ---- NODE 2: RETRIEVE ----
    retrieved_items: List[RetrievedItem]
    retrieval_best_distance: float

    # ---- NODE 3: GENERATE_SQL ----
    generated_sql: str
    chart_type: str                     # 'kpi_card' | 'line' | 'bar' | 'table'
    sql_explanation: str                # what the SQL is trying to answer

    # ---- NODE 4: EXECUTE_SQL ----
    query_result_df: Optional[Any]      # pandas.DataFrame; Any to keep TypedDict simple
    query_result_rows: int
    execute_error: Optional[str]

    # ---- NODE 5: REPAIR (loop control) ----
    retry_count: int

    # ---- NODE 6: NARRATE ----
    narrative: str
    suggested_followups: List[str]

    # ---- META / OBSERVABILITY ----
    total_tokens: int
    total_cost_usd: float
    trace: List[str]                    # append-only log for debugging