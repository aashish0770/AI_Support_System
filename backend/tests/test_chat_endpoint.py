# backend/tests/test_chat_endpoint.py

from fastapi.testclient import TestClient

import app.api.chat as chat_module
from app.db.session import get_db
from app.main import app
from app.services.rag.rag_service import Citation, RAGAnswer

# Overriding get_db avoids needing a real Postgres connection for these
# contract tests — the fake answer_question below never touches the db
# argument anyway, so a real session would be dead weight here.
app.dependency_overrides[get_db] = lambda: None


def test_chat_endpoint_returns_answer_and_citations(monkeypatch):
    def fake_answer_question(db, query, top_k=5):
        return RAGAnswer(
            answer="You can rotate your API key from Settings → API Keys.",
            citations=[
                Citation(
                    chunk_id=1,
                    document_title="Authentication & API Keys",
                    relevance_score=0.032,
                )
            ],
        )

    monkeypatch.setattr(chat_module, "answer_question", fake_answer_question)

    client = TestClient(app)
    response = client.post("/chat", json={"message": "how do I rotate my api key"})

    assert response.status_code == 200
    body = response.json()
    assert "API Keys" in body["answer"] or "Settings" in body["answer"]
    assert body["citations"][0]["document_title"] == "Authentication & API Keys"


def test_chat_endpoint_rejects_empty_message():
    client = TestClient(app)
    response = client.post("/chat", json={"message": ""})

    assert response.status_code == 422


def test_chat_endpoint_response_includes_request_id_header(monkeypatch):
    def fake_answer_question(db, query, top_k=5):
        return RAGAnswer(answer="test", citations=[])

    monkeypatch.setattr(chat_module, "answer_question", fake_answer_question)

    client = TestClient(app)
    response = client.post("/chat", json={"message": "test"})

    assert "X-Request-ID" in response.headers
