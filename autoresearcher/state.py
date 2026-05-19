"""Typed graph state shared across all agent nodes."""
from __future__ import annotations

from operator import add
from typing import Annotated, List, TypedDict


class Source(TypedDict):
    title: str
    url: str
    snippet: str


class ResearchState(TypedDict, total=False):
    # Inputs
    query: str
    max_iterations: int

    # Planning
    sub_questions: List[str]

    # Research outputs (accumulated across iterations)
    evidence: Annotated[List[dict], add]
    sources: Annotated[List[Source], add]

    # Drafting / critique loop
    draft: str
    critique: str
    approved: bool
    iteration: int

    # Final
    report: str
