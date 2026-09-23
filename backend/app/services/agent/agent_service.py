# backend/app/services/agent/agent_service.py

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.services.agent.graph import build_agent_graph

_agent_graph = build_agent_graph()  # built once at import, not per-request


@dataclass
class AgentCitation:
    chunk_id: int
    document_title: str
    relevance_score: float


@dataclass
class AgentAnswer:
    answer: str
    citations: List[AgentCitation] = field(default_factory=list)
    tool_calls_made: List[str] = field(default_factory=list)


def _extract_citations(messages: list) -> List[AgentCitation]:
    citations: List[AgentCitation] = []
    for message in messages:
        if not isinstance(message, ToolMessage) or message.name != "search_docs":
            continue
        try:
            payload = json.loads(message.content)
        except (json.JSONDecodeError, TypeError):
            continue
        if not payload.get("found"):
            continue
        for result in payload.get("results", []):
            citations.append(
                AgentCitation(
                    chunk_id=result["chunk_id"],
                    document_title=result["document_title"],
                    relevance_score=result["relevance_score"],
                )
            )
    return citations


def _extract_tool_names(messages: list) -> List[str]:
    names = []
    for message in messages:
        if isinstance(message, AIMessage) and getattr(message, "tool_calls", None):
            names.extend(tc["name"] for tc in message.tool_calls)
    return names


def run_agent(user_message: str) -> AgentAnswer:
    result = _agent_graph.invoke({"messages": [HumanMessage(content=user_message)]})
    messages = result["messages"]
    final_message = messages[-1]

    return AgentAnswer(
        answer=final_message.content,
        citations=_extract_citations(messages),
        tool_calls_made=_extract_tool_names(messages),
    )
