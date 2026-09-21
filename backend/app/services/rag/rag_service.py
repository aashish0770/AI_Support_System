# backend/app/services/rag/rag_service.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.enums import DocumentSourceType
from app.services.llm import get_llm_provider
from app.services.retrieval.hybrid_search import hybrid_search
from app.services.retrieval.vector_search import vector_search

TOP_K = 5

# Cosine distance from Chroma (collection uses hnsw:space=cosine). 0.0 = identical, higher = less related.
# This is checked BEFORE trusting retrieval as real grounding
# RRF's fused score below can't be user for this, since its rank based and produces
# simila looking number whether the top hit is a great match or a total miss.

OUT_OF_SCOPE_DISTANCE_THRESHOLD = 0.55

SYSTEM_PROMPT = (
    "You are a helpful, personable support assistant for Cobalt Loop, a "
    "workflow-automation platform. Answer the user's question using ONLY "
    "the context provided below, never guess or use outside knowledge. "
    "If the context only partially covers the question, say what you do "
    "know and note what's missing, rather than refusing outright. Keep "
    "answers concise, practical, and conversational."
)

OUT_OF_SCOPE_SYSTEM_PROMPT = (
    "You are a support assistant for Cobalt Loop, a workflow-automation "
    "platform. The user just asked something unrelated to Cobalt Loop or "
    "its documentation. Reply with ONE short, warm sentence acknowledging "
    "that — a touch of light, self-aware humor is welcome, but keep it "
    "brief and don't be sarcastic or dismissive. Do not attempt to answer "
    "the actual question, and do not list any topics or documentation — "
    "that will be added separately."
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
    in_scope: bool = True
    suggested_topics: List[str] = field(default_factory=list)


def _is_out_of_scope(vector_results: List[dict]) -> bool:
    if not vector_results:
        return True
    best_distance = min(r["distance"] for r in vector_results)
    return best_distance > OUT_OF_SCOPE_DISTANCE_THRESHOLD


def _get_all_topic_titles(db: Session) -> List[str]:
    """Only markdown docs, not tickets: ticket titles are issue
    descriptions, not topics names someone would recognize as a thing to as about"""
    rows = db.execute(
        select(Document.title)
        .where(Document.source_type == DocumentSourceType.markdown)
        .order_by(Document.title)
    ).all()
    return [row.title for row in rows]


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
    # Check relevence BEFORE trusting anything as grounding
    # see the thershold constant's comment for why this has to use raw vector distance
    # rather than hybrid_search's fused score
    vector_results = vector_search(query, top_k=top_k)
    if _is_out_of_scope(vector_results):
        llm = get_llm_provider()
        acknowledgement = llm.generate(OUT_OF_SCOPE_SYSTEM_PROMPT, query)
        return RAGAnswer(
            answer=acknowledgement,
            citations=[],
            in_scope=False,
            suggested_topics=_get_all_topic_titles(db),
        )

    #  its an extra embedding call fine for now but if the latency for /chat
    # to be optimizing, the fix is refactoring hybrid_search to accept:
    # pre-computed vector_results instead of calling above vector_search internally
    # this part is for later not Now
    results = hybrid_search(db, query, top_k=top_k)
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

    return RAGAnswer(answer=answer_text, citations=citations, in_scope=True)
