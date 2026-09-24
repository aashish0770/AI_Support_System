# backend/app/services/agent/graph.py

from __future__ import annotations

# from functools import lru_cache
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.core.config import get_settings
from app.services.agent.tools import AVAILABLE_TOOLS

SYSTEM_PROMPT = (
    "You are a helpful, personable support assistant for Cobalt Loop, a "
    "workflow-automation platform.\n\n"
    "Tools available:\n"
    "- search_docs: 'how does X work', 'why is X happening', or anything "
    "answerable from documentation.\n"
    "- check_ticket_status: the user asks about a specific ticket's status.\n"
    "- get_service_health: the user asks if something is down or degraded.\n\n"
    "If a tool reports nothing relevant was found, say so plainly — don't "
    "guess or use outside knowledge. For a question with no plausible "
    "connection to Cobalt Loop at all, a touch of light, self-aware humor "
    "before redirecting is fine — but don't call a tool for it, and don't "
    "attempt to actually answer it.\n\n"
    "Only call one tool at a time, and only when you need information you "
    "don't already have. Once you have enough to answer, respond directly."
)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# @lru_cache
def _get_agent_llm():
    settings = get_settings()
    llm = ChatOllama(
        model=settings.ollama_model, base_url=settings.ollama_base_url, temperature=0.2
    )
    return llm.bind_tools(AVAILABLE_TOOLS)


async def _agent_node(state: AgentState) -> dict:
    # The system prompt is prepended fresh on every call rather than
    # stored in state — this keeps it out of the persisted message
    # history (so it's never duplicated across loop iterations) while
    # still being present for every LLM call.
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    response = await _get_agent_llm().ainvoke(messages)
    return {"messages": [response]}


def _should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


def build_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", _agent_node)
    graph.add_node("tools", ToolNode(AVAILABLE_TOOLS))

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", _should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()
