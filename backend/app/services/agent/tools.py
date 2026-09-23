# backend/app/services/agent/tools.py

from __future__ import annotations

import json

from typing import List

from langchain_core.tools import tool
from sqlalchemy import select

from app.db.session import get_session
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.ticket import Ticket
from app.services.agent.tool_schemas import DocExcerpt, SearchDocsResponse
from app.services.retrieval.hybrid_search import hybrid_search
from app.services.retrieval.vector_search import vector_search

# Same threshold and reasoning as rag_service — kept here since
# this is now the tool's own responsibility to signal relevance, not an
# external pre-check. See rag_service.py's comment for why this must use
# raw vector distance, not hybrid_search's rank-based RRF score.
OUT_OF_SCOPE_DISTANCE_THRESHOLD = 0.55

TOP_K = 5


# Mock, in-memory — there's no real service-health table to back this
# with (unlike tickets), and building one would be its own scope decision
# outside what this tool needs to demonstrate.
_MOCK_SERVICE_STATUS = {
    "api": "operational",
    "webhooks": "operational",
    "dashboard": "operational",
    "workflow_engine": "operational",
}


def _tool_by_chunk_id(db, chunk_ids: List[int]) -> dict:
    if not chunk_ids:
        return {}

    rows = db.execute(
        select(Chunk.id, Document.title)
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.id.in_(chunk_ids))
    ).all()

    return {row.id: row.title for row in rows}


@tool
def search_docs(query: str) -> str:
    """Search Cobalt Loop's documentation and past support tickets for information relevant to the user's question.

    Use this whenever the user asks how something works, why something might be happening,
    or anything answerable from product documentation.
    """
    db = get_session()

    try:
        vec_results = vector_search(query, top_k=TOP_K)

        if (
            not vec_results
            or min(r["distance"] for r in vec_results) > OUT_OF_SCOPE_DISTANCE_THRESHOLD
        ):
            return json.dumps(
                {
                    "found": False,
                    "message": "No relevant documentation found for this query.",
                }
            )

        results = hybrid_search(db, query, top_k=TOP_K)

        title_by_id = _tool_by_chunk_id(
            db,
            [r["chunk_id"] for r in results],
        )

        excerpts: List[DocExcerpt] = [
            DocExcerpt(
                chunk_id=r["chunk_id"],
                document_title=title_by_id.get(
                    r["chunk_id"],
                    "Unknown source",
                ),
                content=r["content"],
                relevance_score=r["score"],
            )
            for r in results
        ]

        payload: SearchDocsResponse = {
            "found": True,
            "results": excerpts,
        }

        return json.dumps(payload)

    finally:
        db.close()


@tool
def check_ticket_status(subject_keyword: str) -> str:
    """Look up the status of a support ticket by a keyword from its subject line.

    Use this when the user asks about the status of a specific issue or ticket they've raised,
    rather than a general question.
    """
    db = get_session()

    try:
        ticket = (
            db.query(Ticket)
            .filter(Ticket.subject.ilike(f"%{subject_keyword}%"))
            .order_by(Ticket.created_at.desc())
            .first()
        )

        if not ticket:
            return json.dumps(
                {
                    "found": False,
                    "message": f"No ticket found matching '{subject_keyword}'.",
                }
            )

        return json.dumps(
            {
                "found": True,
                "subject": ticket.subject,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat(),
            }
        )

    finally:
        db.close()


@tool
def get_service_health() -> str:
    """Check the current operational status of the service.

    (API, webhooks, dashboard, workflow engine)
    Use this when the user asks if something is down, degraded, or experiencing an outage.
    """
    return json.dumps(_MOCK_SERVICE_STATUS)


AVAILABLE_TOOLS = [
    search_docs,
    check_ticket_status,
    get_service_health,
]
