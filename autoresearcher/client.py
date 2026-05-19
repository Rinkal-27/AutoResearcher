"""MCP client helpers — talk to the deployed AutoResearcher MCP server over
Streamable HTTP using the official `mcp` Python SDK.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Dict

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


@asynccontextmanager
async def mcp_session(url: str):
    """Async context manager yielding an initialized MCP ClientSession."""
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def list_tools(url: str) -> list[dict]:
    async with mcp_session(url) as session:
        tools = await session.list_tools()
        return [
            {"name": t.name, "description": t.description or ""}
            for t in tools.tools
        ]


async def call_tool(url: str, name: str, arguments: Dict[str, Any]) -> str:
    async with mcp_session(url) as session:
        result = await session.call_tool(name, arguments)
        parts: list[str] = []
        for c in result.content:
            text = getattr(c, "text", None)
            if text:
                parts.append(text)
        return "\n".join(parts)
