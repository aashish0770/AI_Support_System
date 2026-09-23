from fastapi.testclient import TestClient

import app.api.chat as chat_module
from app.main import app
from app.services.agent.agent_service import AgentAnswer, AgentCitation


def test_chat_endpoint_returns_answer_and_citations(monkeypatch):
    def fake_run_agent(message):
        return AgentAnswer(
            answer="You can rotate your API key from Settings → API Keys.",
            citations=[
                AgentCitation(
                    chunk_id=1,
                    document_title="Authentication & API Keys",
                    relevance_score=0.032,
                )
            ],
            tool_calls_made=["search_docs"],
        )

    monkeypatch.setattr(chat_module, "run_agent", fake_run_agent)

    client = TestClient(app)
    response = client.post("/chat", json={"message": "how do I rotate my api key"})

    assert response.status_code == 200
    assert (
        response.json()["citations"][0]["document_title"] == "Authentication & API Keys"
    )


def test_chat_endpoint_rejects_empty_message():
    client = TestClient(app)
    assert client.post("/chat", json={"message": ""}).status_code == 422
