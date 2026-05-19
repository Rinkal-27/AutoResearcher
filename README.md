# AutoResearcher

A multi-agent research assistant that turns a single question into a fully cited Markdown report.

A **Planner** breaks the question into focused sub-questions, a **Researcher** gathers evidence from the web, a **Writer** drafts a structured report with inline citations, and a **Critic** fact-checks the draft against the evidence. If the Critic spots unsupported claims it sends the Researcher back for another pass — the loop runs until the report is grounded or `max_iterations` is reached.

```
                 ┌───────────┐
        query ─▶ │  Planner  │── sub-questions ─┐
                 └───────────┘                  ▼
                                          ┌────────────┐
                                          │ Researcher │◀── Tavily web search
                                          └────────────┘
                                                │
                                                ▼
                                          ┌──────────┐
                                          │  Writer  │── draft ─┐
                                          └──────────┘          ▼
                                                ▲        ┌──────────┐
                                                └────────│  Critic  │
                                                 revise  └──────────┘
                                                                │
                                                                ▼
                                                         final report
```

## Stack

- **LangGraph** — stateful multi-agent orchestration with a Critic loop
- **Groq Llama 3.3-70B** — fast, free LLM inference
- **Tavily** — LLM-friendly web search for evidence gathering
- **FastMCP** with **Streamable HTTP** transport — exposes the pipeline as MCP tools
- **Streamlit** — UI that talks to the MCP server as a real MCP client

## MCP tools exposed

| Tool | Description |
| --- | --- |
| `research(query, max_iterations=3)` | Full pipeline → cited Markdown report |
| `quick_search(query, max_results=5)` | Single Tavily search, raw JSON results |

## Live demo

- **Streamlit app:** https://autoresearcher-mqkxeimrurndr7zeffdwcv.streamlit.app/
- **MCP endpoint:** `https://autoresearcher-bwre.onrender.com/mcp`

You can point any MCP-aware client (Claude Desktop, Cursor, VS Code, or the Streamlit UI in this repo) at the MCP endpoint above — no local setup required.

For Claude Desktop add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "autoresearcher": {
      "transport": "http",
      "url": "https://autoresearcher-bwre.onrender.com/mcp"
    }
  }
}
```

> The host sleeps after inactivity; the first request may take ~30s to wake.

## Run locally

Prerequisites: Python 3.11, a free Groq API key (https://console.groq.com), a free Tavily key (https://tavily.com).

```powershell
cd projects/autoresearcher
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
# Edit .env and fill in GROQ_API_KEY and TAVILY_API_KEY
```

### Option 1 — CLI

```powershell
python -m autoresearcher.cli "What are the latest advances in Model Context Protocol?"
```

### Option 2 — Local MCP server

```powershell
python -m autoresearcher.mcp_server
# Streamable HTTP endpoint: http://localhost:8000/mcp
```

### Option 3 — Streamlit UI (MCP client)

```powershell
streamlit run streamlit_app.py
```

In the sidebar, set the **MCP server URL** to either:
- `http://localhost:8000/mcp` (your local server), or
- `https://autoresearcher-bwre.onrender.com/mcp` (the hosted instance).

## Project layout

```
autoresearcher/
  state.py        # Typed LangGraph state
  llm.py          # Groq Llama factory
  tools.py        # Tavily web search wrapper
  agents.py       # Planner / Researcher / Writer / Critic nodes
  graph.py        # LangGraph wiring + run_research()
  mcp_server.py   # FastMCP server (streamable HTTP)
  client.py       # MCP client helpers (used by Streamlit)
  cli.py          # CLI entrypoint
streamlit_app.py  # MCP-client UI
```
