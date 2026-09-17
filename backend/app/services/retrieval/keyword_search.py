# backend/app/services/retrieval/keyword_search.py

from __future__ import annotations

from typing import List, TypedDict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk


class KeywordSearchResult(TypedDict):
    chunk_id: int
    content: str
    rank: float


def keyword_search(
    db: Session, query: str, top_k: int = 5
) -> List[KeywordSearchResult]:
    query = query.strip()
    if not query:
        # plainto_tsquery('') produces an empty tsquery that matches
        # nothing predictably — short-circuit rather than let an empty
        # query silently return an empty or undefined result set.
        return []

    ts_query = func.plainto_tsquery("english", query)
    rank = func.ts_rank(Chunk.tsv, ts_query, 1).label("rank")

    stmt = (
        select(Chunk.id, Chunk.content, rank)
        .where(Chunk.tsv.op("@@")(ts_query))
        .order_by(rank.desc())
        .limit(top_k)
    )

    rows = db.execute(stmt).all()
    return [
        KeywordSearchResult(chunk_id=row.id, content=row.content, rank=float(row.rank))
        for row in rows
    ]
