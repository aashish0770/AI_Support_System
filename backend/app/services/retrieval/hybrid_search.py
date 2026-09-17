# backend/app/services/retrieval/hybrid_search.py

from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from app.services.retrieval.fusion import FusedResult, reciprocal_rank_fusion
from app.services.retrieval.keyword_search import keyword_search
from app.services.retrieval.vector_search import vector_search


def hybrid_search(db: Session, query: str, top_k: int = 5) -> List[FusedResult]:
    vector_results = vector_search(query, top_k=top_k)
    keyword_results = keyword_search(db, query, top_k=top_k)

    vector_ranked = [
        {"chunk_id": r["chunk_id"], "content": r["content"]} for r in vector_results
    ]
    keyword_ranked = [
        {"chunk_id": r["chunk_id"], "content": r["content"]} for r in keyword_results
    ]

    return reciprocal_rank_fusion([vector_ranked, keyword_ranked])[:top_k]
