"""LLM factory — Groq Llama 3.3-70B (free tier)."""
from __future__ import annotations

import os

from langchain_groq import ChatGroq


def get_llm(temperature: float = 0.2) -> ChatGroq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")
    model = os.environ.get("MODEL_NAME", "llama-3.3-70b-versatile")
    return ChatGroq(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_retries=2,
    )
