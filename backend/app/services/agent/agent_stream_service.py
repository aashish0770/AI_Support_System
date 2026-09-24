# backend/app/services/agent/agent_stream_service.py

from __future__ import annotations

import json
from typing import AsyncGenerator
from loguru import logger

from langchain_core.messages import HumanMessage

from app.services.agent.agent_service import (
    extract_citations,
    extract_tool_names,
    _agent_graph,
)


async def stream_agent(user_message: str) -> AsyncGenerator[dict, None]:
    """
    Yields Server-Sent Events(SSE) ready dicts: {"event": <type>, "data": <value>}
    Event types:
      - "token"      : a piece of the final answer's text, as it's generated
      - "tool_start" : the agent has decided to call a tool (name in data)
      - "tool_end"   : that tool call has finished (name in data)
      - "done"       : streaming complete — carries full citations + tool list
      - "error"      : something went wrong mid-stream

    Design note (see Week 8 writeup): tool-call arguments arrive as
    streamed chunks with EMPTY .content — the actual tool-call data lives
    in .tool_call_chunks instead. That's the mechanism this relies on to
    only forward real prose tokens, never partial tool-call JSON.
    """

    inputs = {"messages": [HumanMessage(content=user_message)]}
    all_messages: list = []

    try:
        async for event in _agent_graph.astream_events(inputs, version="v2"):
            kind = event["event"]

            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    yield {"event": "token", "data": chunk.content}

            elif kind == "on_tool_start":
                yield {
                    "event": "tool_start",
                    "data": json.dumps({"tool": event["name"]}),
                }

            elif kind == "on_tool_end":
                yield {"event": "tool_end", "data": json.dumps({"tool": event["name"]})}

            elif kind == "on_chain_end" and not event.get("parent_ids"):
                # Root-level chain end == the whole graph invocation just
                # finished. Checking "no parent_ids" rather than matching
                # a hardcoded graph name is what makes this robust
                # regardless of how the graph gets compiled/named.
                output = event["data"].get("output")
                if isinstance(output, dict) and "messages" in output:
                    all_messages = output["messages"]

    except Exception:
        logger.exception("Agent stream failed.")
        yield {
            "event": "error",
            "data": "An internal error occurred while processing your request. Please try again.",
        }
        return

    yield {
        "event": "done",
        "data": json.dumps(
            {
                "citations": [
                    {
                        "chunk_id": c.chunk_id,
                        "document_title": c.document_title,
                        "relevance_score": c.relevance_score,
                    }
                    for c in extract_citations(all_messages)
                ],
                "tool_calls_made": extract_tool_names(all_messages),
            }
        ),
    }
