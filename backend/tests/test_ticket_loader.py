# backend/tests/test_ticket_loader.py
import json

import pytest

from app.models.document import Document
from app.models.enums import DocumentSourceType, DocumentStatus
from app.services.ingestion.ticket_loader import TicketLoader


@pytest.fixture()
def sample_tickets_dir(tmp_path, monkeypatch):
    tickets_dir = tmp_path / "tickets"
    tickets_dir.mkdir()

    sample_tickets = [
        {
            "subject": "Webhook signature always fails",
            "description": "Hashing the re-serialized body instead of raw bytes.",
            "status": "resolved",
            "priority": "high",
            "created_at": "2026-02-03T14:12:00Z",
            "resolution_notes": "Told them to hash raw request body.",
        },
        {
            "subject": "Workflow not firing",
            "description": "New rows aren't triggering anything.",
            "status": "open",
            "priority": "high",
            "created_at": "2026-02-14T10:00:00Z",
            "resolution_notes": None,  # explicit null — this is the case that used to crash
        },
    ]

    (tickets_dir / "tickets.json").write_text(
        json.dumps(sample_tickets), encoding="utf-8"
    )

    import app.services.ingestion.ticket_loader as loader_module

    monkeypatch.setattr(loader_module, "TICKET_PATH", tickets_dir)
    return tickets_dir


def test_normalize_ticket_handles_null_resolution_notes():
    loader = TicketLoader()
    ticket = {
        "subject": "Test subject",
        "description": "Test description",
        "resolution_notes": None,
        "status": "open",
        "priority": "medium",
        "created_at": "2026-01-01T00:00:00Z",
    }

    normalized = loader._normalize_ticket(ticket)

    assert normalized["title"] == "Test subject"
    assert "Test description" in normalized["content"]
    assert normalized["metadata"]["status"] == "open"


def test_normalize_ticket_handles_explicit_null_subject():
    """This is the case that would previously crash with AttributeError
    before subject/description got the same None-guard as resolution_notes."""
    loader = TicketLoader()
    ticket = {"subject": None, "description": None, "resolution_notes": None}

    normalized = loader._normalize_ticket(ticket)

    assert normalized["title"] == "Untitled Ticket"


def test_ingest_creates_documents_from_json(db_session, sample_tickets_dir):
    loader = TicketLoader()

    ingested = loader.ingest(db_session)

    assert ingested == 2
    documents = db_session.query(Document).all()
    assert len(documents) == 2
    assert all(doc.source_type == DocumentSourceType.ticket for doc in documents)
    assert all(doc.status == DocumentStatus.pending for doc in documents)


def test_ingest_is_idempotent(db_session, sample_tickets_dir):
    loader = TicketLoader()

    first_run = loader.ingest(db_session)
    second_run = loader.ingest(db_session)

    assert first_run == 2
    assert second_run == 0
