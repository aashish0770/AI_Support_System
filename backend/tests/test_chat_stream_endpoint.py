# backend/app/tests/test_chat_endpoint.py

import json

from fastapi.testclient import TestClient

import app.api.chat as chat_module
from app.main import app


def test_chat_stream_endpoint_yields_tokens_and_done_event(monkeypatch):
    async def fake_stream_agent(message):
        yield {"event": "token", "data": "Hello"}
        yield {"event": "token", "data": " world"}
        yield {
            "event": "done",
            "data": json.dumps({"citations": [], "tool_calls_made": []}),
        }

    monkeypatch.setattr(chat_module, "stream_agent", fake_stream_agent)

    client = TestClient(app)
    with client.stream("POST", "/chat/stream", json={"message": "hi"}) as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())

    assert "event: token" in body
    assert "Hello" in body
    assert "event: done" in body


def test_chat_stream_endpoint_forwards_tool_events(monkeypatch):
    async def fake_stream_agent(message):
        yield {"event": "tool_start", "data": json.dumps({"tool": "search_docs"})}
        yield {"event": "token", "data": "answer"}
        yield {"event": "tool_end", "data": json.dumps({"tool": "search_docs"})}
        yield {
            "event": "done",
            "data": json.dumps({"citations": [], "tool_calls_made": ["search_docs"]}),
        }

    monkeypatch.setattr(chat_module, "stream_agent", fake_stream_agent)

    client = TestClient(app)
    with client.stream("POST", "/chat/stream", json={"message": "hi"}) as response:
        body = "".join(response.iter_text())

    assert "event: tool_start" in body
    assert "event: tool_end" in body
