# AutoResearcher

Multi-agent research and report-generation system.

- **LangGraph** state machine (Planner → Researcher → Writer → Critic loop)
- **Free LLM**: Llama 3.3-70B via **Groq**
- **FastMCP** server with **Streamable HTTP** transport
- **Streamlit** UI that calls the deployed MCP server as a real MCP client
- 100% free-tier deployable: Groq + Tavily free + Render free web service + Streamlit Community Cloud

```
                 ┌───────────┐
        query ─▶ │  Planner  │── sub-questions ─┐
                 └───────────┘                  ▼
                                          ┌────────────┐
                                          │ Researcher │◀── Tavily
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

## Local quick start

```powershell
cd projects/autoresearcher
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# edit .env: GROQ_API_KEY (free at console.groq.com), TAVILY_API_KEY (free at tavily.com)

# 1) Run MCP server (streamable HTTP on http://localhost:8000/mcp)
python -m autoresearcher.mcp_server

# 2) In another shell, run the Streamlit client
streamlit run streamlit_app.py
```

Point the Streamlit UI's "MCP server URL" field to your local or deployed URL.

## Free deployment

### MCP server → Render.com (free web service)

1. Push this folder to a GitHub repo.
2. On https://render.com → **New + → Web Service** → connect repo.
3. Render auto-detects [render.yaml](render.yaml). Set env vars `GROQ_API_KEY` and `TAVILY_API_KEY` in the dashboard.
4. After deploy, your MCP endpoint is `https://<service>.onrender.com/mcp`.

> The free tier spins down after 15 min of inactivity (first request after that takes ~30s to wake up).

Alternatives: **Fly.io** (free allowance), **Railway** (trial credits), **Hugging Face Spaces** Docker SDK.

### Streamlit UI → Streamlit Community Cloud (free)

1. Push this folder to GitHub (same or separate repo).
2. https://share.streamlit.io → **New app** → point to [streamlit_app.py](streamlit_app.py).
3. In **Advanced settings → Secrets**, paste:
   ```toml
   MCP_URL = "https://<your-render-service>.onrender.com/mcp"
   ```
4. Deploy. Done.

## MCP client config (Claude Desktop / Cursor / VS Code)

Once deployed, any MCP-aware client can use the streamable-HTTP URL directly. For Claude Desktop add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "autoresearcher": {
      "transport": "http",
      "url": "https://<your-render-service>.onrender.com/mcp"
    }
  }
}
```

## Tools exposed by the MCP server

- `research(query, max_iterations=3)` → full cited Markdown report
- `quick_search(query, max_results=5)` → raw Tavily results
