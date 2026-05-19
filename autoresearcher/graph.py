"""LangGraph wiring for the AutoResearcher state machine."""
from __future__ import annotations

import os
from typing import Any, Dict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from .agents import (
    critic_node,
    finalize_node,
    planner_node,
    researcher_node,
    writer_node,
)
from .state import ResearchState

load_dotenv()


def _should_continue(state: ResearchState) -> str:
    if state.get("approved"):
        return "finalize"
    if state.get("iteration", 0) >= state.get("max_iterations", 3):
        return "finalize"
    return "researcher"


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)
    graph.add_node("finalize", finalize_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges(
        "critic",
        _should_continue,
        {"researcher": "researcher", "finalize": "finalize"},
    )
    graph.add_edge("finalize", END)
    return graph.compile()


def run_research(query: str, max_iterations: int | None = None) -> Dict[str, Any]:
    app = build_graph()
    max_iter = max_iterations or int(os.environ.get("MAX_ITERATIONS", "3"))
    initial: ResearchState = {
        "query": query,
        "max_iterations": max_iter,
        "evidence": [],
        "sources": [],
    }
    final_state = app.invoke(initial)
    return {
        "query": query,
        "report": final_state.get("report", ""),
        "iterations": final_state.get("iteration", 0),
        "approved": final_state.get("approved", False),
        "sources": final_state.get("sources", []),
    }
