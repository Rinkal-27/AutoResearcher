"""Agent node implementations: Planner, Researcher, Critic, Writer."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from .llm import get_llm
from .state import ResearchState, Source
from .tools import web_search


def _extract_json_array(text: str) -> List[str]:
    match = re.search(r"\[.*?\]", text, flags=re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            return [str(x) for x in data if str(x).strip()]
        except json.JSONDecodeError:
            pass
    return [line.strip("-* \t") for line in text.splitlines() if line.strip()]


def _format_sources(sources: List[Source]) -> str:
    return "\n".join(
        f"[{i + 1}] {s['title']} — {s['url']}\n    {s['snippet'][:300]}"
        for i, s in enumerate(sources)
    )


def planner_node(state: ResearchState) -> Dict[str, Any]:
    llm = get_llm(temperature=0.1)
    messages = [
        SystemMessage(
            content=(
                "You decompose a research question into 3-5 focused, non-overlapping "
                "sub-questions. Reply ONLY with a JSON array of strings."
            )
        ),
        HumanMessage(content=f"Research question:\n{state['query']}"),
    ]
    resp = llm.invoke(messages)
    sub_questions = _extract_json_array(resp.content)[:5]
    return {"sub_questions": sub_questions, "iteration": 0}


def researcher_node(state: ResearchState) -> Dict[str, Any]:
    llm = get_llm(temperature=0.2)
    sub_questions = state.get("sub_questions", [])
    critique = state.get("critique", "")

    targets = (
        [critique] if critique and state.get("iteration", 0) > 0 else sub_questions
    )

    new_evidence: List[dict] = []
    new_sources: List[Source] = []
    for q in targets:
        sources = web_search(q, max_results=4)
        new_sources.extend(sources)
        messages = [
            SystemMessage(
                content=(
                    "Synthesize a concise (<=200 words) factual answer to the question "
                    "using ONLY the provided sources. Cite sources inline as [1], [2], ..."
                )
            ),
            HumanMessage(
                content=f"Question: {q}\n\nSources:\n{_format_sources(sources)}"
            ),
        ]
        resp = llm.invoke(messages)
        new_evidence.append({"question": q, "findings": resp.content})

    return {"evidence": new_evidence, "sources": new_sources}


def writer_node(state: ResearchState) -> Dict[str, Any]:
    llm = get_llm(temperature=0.3)
    evidence = state.get("evidence", [])
    sources = state.get("sources", [])

    evidence_block = "\n\n".join(
        f"### {e['question']}\n{e['findings']}" for e in evidence
    )
    sources_block = "\n".join(
        f"[{i + 1}] {s['title']} — {s['url']}" for i, s in enumerate(sources)
    )

    messages = [
        SystemMessage(
            content=(
                "You are a senior technical writer. Produce a well-structured Markdown "
                "report with: Title, Executive Summary, Key Findings (with inline "
                "citations like [1]), Analysis, and References. Be precise; do not "
                "invent facts beyond the evidence."
            )
        ),
        HumanMessage(
            content=(
                f"Research question: {state['query']}\n\n"
                f"Evidence:\n{evidence_block}\n\n"
                f"Sources:\n{sources_block}"
            )
        ),
    ]
    resp = llm.invoke(messages)
    return {"draft": resp.content}


def critic_node(state: ResearchState) -> Dict[str, Any]:
    llm = get_llm(temperature=0.0)
    messages = [
        SystemMessage(
            content=(
                "You are a rigorous fact-checking critic. Review the draft against the "
                "evidence and decide if every claim is supported. Reply with strict JSON:\n"
                '{"approved": true|false, "missing": "concise description of the single '
                'most important gap to research next, or empty string if approved"}'
            )
        ),
        HumanMessage(
            content=(
                f"Question: {state['query']}\n\n"
                f"Draft:\n{state.get('draft', '')}\n\n"
                f"Evidence:\n{json.dumps(state.get('evidence', []), indent=2)[:6000]}"
            )
        ),
    ]
    resp = llm.invoke(messages)
    approved = False
    missing = ""
    try:
        match = re.search(r"\{.*\}", resp.content, flags=re.DOTALL)
        data = json.loads(match.group(0)) if match else {}
        approved = bool(data.get("approved", False))
        missing = str(data.get("missing", "")).strip()
    except (json.JSONDecodeError, AttributeError):
        approved = "approved" in resp.content.lower()

    return {
        "approved": approved,
        "critique": missing,
        "iteration": state.get("iteration", 0) + 1,
    }


def finalize_node(state: ResearchState) -> Dict[str, Any]:
    return {"report": state.get("draft", "")}
