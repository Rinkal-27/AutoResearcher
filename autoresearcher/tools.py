"""External tools used by the agents."""
from __future__ import annotations

import os
from typing import List

from tavily import TavilyClient

from .state import Source

_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError("TAVILY_API_KEY is not set")
        _client = TavilyClient(api_key=api_key)
    return _client


def web_search(query: str, max_results: int = 5) -> List[Source]:
    """Return a list of Source dicts for the given query."""
    resp = _get_client().search(
        query=query,
        max_results=max_results,
        search_depth="advanced",
        include_answer=False,
    )
    out: List[Source] = []
    for r in resp.get("results", []):
        out.append(
            Source(
                title=r.get("title", "")[:200],
                url=r.get("url", ""),
                snippet=r.get("content", "")[:1000],
            )
        )
    return out
