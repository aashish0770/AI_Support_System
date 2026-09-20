# backend/app/services/rag/rag_service.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.llm import get_llm_provider
from app.services.retrieval.hybrid_search import hybrid_search

TOP_K = 5

SYSTEM_PROMPT = (
    "You are a support assistant for Cobalt Loop, a workflow-automation"
    "platform. Answer the user's question using ONLY the context provided"
    "below. If the context doesn't contain enough information to answer,"
    "say so plainly rather than guessing or using outside knowledge. Kepp"
    "answers concise and practical."
)


@dataclass
class Citation:
    chunk_id = int
    document_title = str
    relevance_score = float


@dataclass
class RAGAnswer:
    answer = str
    citations = List[Citation]


def _title_by_chunk_id(db: Session, chunk_ids: List[int]) -> dict:
    if not chunk_ids:
        return {}
    rows = db.execute(
        select(Chunk.id, Document.title)
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.id.in_(chunk_ids))
    ).all()
    return {row.id: row.title for row in rows}
