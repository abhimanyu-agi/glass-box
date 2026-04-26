"""
Shared OpenAI client + helpers for cost/token tracking.

All nodes call these helpers instead of the OpenAI client directly.
This gives us one place to swap models, add retries, or track cost.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Approximate pricing (USD per 1M tokens), used for rough cost tracking.
# Source: OpenAI pricing page — update when prices change.
PRICING = {
    "gpt-4o":               {"in": 2.50, "out": 10.00},
    "gpt-4o-mini":          {"in": 0.15, "out": 0.60},
    "text-embedding-3-small": {"in": 0.02, "out": 0.00},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    p = PRICING.get(model, {"in": 0, "out": 0})
    return (input_tokens * p["in"] + output_tokens * p["out"]) / 1_000_000


def chat_completion(
    model: str,
    messages: list,
    response_format: dict | None = None,
    temperature: float = 0.0,
):
    """
    Wrapper around OpenAI chat completions.

    Returns:
        content_str: the assistant's text reply
        usage:       dict with prompt_tokens / completion_tokens / cost_usd
    """
    kwargs = dict(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    if response_format:
        kwargs["response_format"] = response_format

    response = _client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    usage = {
        "prompt_tokens":     response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "cost_usd": estimate_cost(
            model,
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
        ),
    }
    return content, usage


def embed(text: str) -> list[float]:
    """Single-text embedding used by the retrieval node."""
    response = _client.embeddings.create(
        model="text-embedding-3-small",
        input=[text],
    )
    return response.data[0].embedding