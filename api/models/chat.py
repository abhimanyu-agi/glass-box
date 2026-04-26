"""Pydantic schemas for chat endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role:    Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000,
                          description="The user's question in plain English")
    history:  list[ChatMessage] = Field(
        default_factory=list,
        description="Prior conversation turns (most recent last)",
    )