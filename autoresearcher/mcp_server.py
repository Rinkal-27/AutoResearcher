"""FastMCP server exposing AutoResearcher over Streamable HTTP.

Run locally:
    python -m autoresearcher.mcp_server

The server listens on http://HOST:PORT/mcp (defaults: 0.0.0.0:8000).
"""
from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .graph import run_research
from .tools import web_search

load_dotenv()

mcp = FastMCP(
    name="autoresearcher",
    host=os.environ.get("HOST", "0.0.0.0"),
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True,  # friendlier for serverless / free-tier hosts
)


@mcp.tool()
def research(query: str, max_iterations: int = 3) -> str:
    """Run the multi-agent research pipeline and return a cited Markdown report.

    Args:
        query: The research question.
        max_iterations: Max Critic-Researcher refinement loops (1-6).
    """
    max_iterations = max(1, min(int(max_iterations), 6))
    result = run_research(query, max_iterations=max_iterations)
    return result["report"]


@mcp.tool()
def quick_search(query: str, max_results: int = 5) -> str:
    """Run a single web search via Tavily and return raw results as JSON."""
    max_results = max(1, min(int(max_results), 10))
    results = web_search(query, max_results=max_results)
    return json.dumps(results, indent=2)


def main() -> None:
    # FastMCP supports "streamable-http" transport (recommended) or "sse".
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
