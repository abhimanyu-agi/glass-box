"""
Wraps the existing LangGraph agent so the chat router can invoke it.

We build the agent once at module import time (lazy-cached) so every
chat request reuses the same graph.
"""

import functools
import pandas as pd

from agent.graph import build_agent


@functools.lru_cache(maxsize=1)
def _get_agent():
    """Build the LangGraph once. Cached for the life of the process."""
    return build_agent()


def run_agent(question: str, history: list[dict]) -> dict:
    """
    Runs the agent synchronously and returns its final state dict.

    Args:
        question: user's latest question
        history:  list of prior turns, each with {role, content}

    Returns the raw agent state; the router picks what to stream.
    """
    agent = _get_agent()

    # Normalize the DataFrame so it's JSON-serializable later
    result = agent.invoke({
        "question":             question,
        "conversation_history": history,
        "trace":                [],
        "total_cost_usd":       0.0,
        "retry_count":          0,
    })

    return result


def df_to_records(df) -> list[dict]:
    """Safely turn a pandas DataFrame into list-of-dicts, or empty list if None."""
    if df is None:
        return []
    if isinstance(df, pd.DataFrame):
        if len(df) == 0:
            return []
        # Convert date/datetime columns to ISO strings so JSON works
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime("%Y-%m-%d")
        return df.to_dict(orient="records")
    return []