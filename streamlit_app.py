"""Streamlit UI — MCP client for the deployed AutoResearcher server.

Run locally:   streamlit run streamlit_app.py
Deploy free:   share.streamlit.io  (set MCP_URL in app secrets)
"""
from __future__ import annotations

import asyncio
import json
import os

import streamlit as st

from autoresearcher.client import call_tool, list_tools

st.set_page_config(page_title="AutoResearcher", page_icon="🔎", layout="wide")
st.title("🔎 AutoResearcher")

# --- Resolve MCP URL: Streamlit Secrets > env var > sidebar input ---
default_url = (
    st.secrets.get("MCP_URL", None) if hasattr(st, "secrets") else None
) or os.environ.get("MCP_URL") or "http://localhost:8000/mcp"

with st.sidebar:
    st.header("MCP server")
    mcp_url = st.text_input("Streamable-HTTP URL", value=default_url)
    if st.button("Ping / list tools"):
        try:
            tools = asyncio.run(list_tools(mcp_url))
            st.success(f"Connected. Tools: {[t['name'] for t in tools]}")
            with st.expander("Tool details"):
                st.json(tools)
        except Exception as e:  # noqa: BLE001
            st.error(f"Failed to connect: {e}")

    st.divider()
    tool_choice = st.radio("Tool", ["research", "quick_search"], index=0)
    max_iter = st.slider("max_iterations (research)", 1, 6, 3)
    max_results = st.slider("max_results (quick_search)", 1, 10, 5)


query = st.text_area(
    "Question",
    height=120,
    placeholder="e.g. What are the latest advances in Model Context Protocol (MCP)?",
)

go = st.button("Run", type="primary", disabled=not query.strip())

if go:
    try:
        with st.spinner("Calling MCP server..."):
            if tool_choice == "research":
                output = asyncio.run(
                    call_tool(
                        mcp_url,
                        "research",
                        {"query": query, "max_iterations": int(max_iter)},
                    )
                )
                st.markdown(output)
            else:
                output = asyncio.run(
                    call_tool(
                        mcp_url,
                        "quick_search",
                        {"query": query, "max_results": int(max_results)},
                    )
                )
                try:
                    st.json(json.loads(output))
                except json.JSONDecodeError:
                    st.code(output)
    except Exception as e:  # noqa: BLE001
        st.error(f"MCP call failed: {e}")
        st.info(
            "If you just deployed to Render's free tier, the service may be "
            "waking up (cold start ~30s). Try again in a moment."
        )
