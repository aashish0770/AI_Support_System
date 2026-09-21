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
    "say so plainly rather than guessing or using outside knowledge. Keep"
    "answers concise and practical."
)


@dataclass
class Citation:
    chunk_id: int
    document_title: str
    relevance_score: float


@dataclass
class RAGAnswer:
    answer: str
    citations: List[Citation]


def _title_by_chunk_id(db: Session, chunk_ids: List[int]) -> dict:
    if not chunk_ids:
        return {}
    rows = db.execute(
        select(Chunk.id, Document.title)
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.id.in_(chunk_ids))
    ).all()
    return {row.id: row.title for row in rows}


def _build_context_block(results: List[dict], title_by_id: dict) -> str:
    parts = []
    for i, result in enumerate(results, start=1):
        title = title_by_id.get(result["chunk_id"], "Unknown source")
        parts.append(f'[{i}] (from "{title}")\n{result["content"]}')
    return "\n\n".join(parts)


def answer_question(db: Session, query: str, top_k: int = TOP_K) -> RAGAnswer:
    results = hybrid_search(db, query, top_k=top_k)

    if not results:
        return RAGAnswer(
            answer="I couldn't find anything relevent to answer that, "
            "could you rephrase or give a bit more detail?",
            citations=[],
        )
    chunk_ids = [r["chunk_id"] for r in results]
    title_by_id = _title_by_chunk_id(db, chunk_ids)

    context_block = _build_context_block(results, title_by_id)
    user_message = f"Context:\n{context_block}\n\nQuestion:\n{query}"

    llm = get_llm_provider()
    answer_text = llm.generate(SYSTEM_PROMPT, user_message)

    citations = [
        Citation(
            chunk_id=r["chunk_id"],
            document_title=title_by_id.get(r["chunk_id"], "Unknown source"),
            relevance_score=r["score"],
        )
        for r in results
    ]

    return RAGAnswer(answer=answer_text, citations=citations)
