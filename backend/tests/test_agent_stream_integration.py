# backend/app/tests/test_agent_stream_integration.py

"""Real Ollama, real Postgres, real Chroma — same caveats as
test_agent_integration.py. Run explicitly with -m integration."""

import asyncio
import json

import pytest

from app.services.agent.agent_stream_service import stream_agent

pytestmark = pytest.mark.integration


def _collect_events(message: str) -> list:
    async def _run():
        return [event async for event in stream_agent(message)]

    return asyncio.run(_run())


def test_docs_question_streams_tokens_and_ends_with_citations():
    events = _collect_events("how do I verify a webhook signature")

    token_events = [e for e in events if e["event"] == "token"]
    done_events = [e for e in events if e["event"] == "done"]

    assert len(token_events) > 1  # actually streamed, not one giant chunk
    assert len(done_events) == 1

    done_payload = json.loads(done_events[0]["data"])
    assert len(done_payload["citations"]) > 0


def test_docs_question_emits_tool_start_and_end():
    events = _collect_events("how do I verify a webhook signature")
    event_types = [e["event"] for e in events]

    assert "tool_start" in event_types
    assert "tool_end" in event_types
