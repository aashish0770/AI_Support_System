# backend/app/services/retrieval/fusion.py

from __future__ import annotations

from typing import Dict, List, TypedDict


class FusedResult(TypedDict):
    chunk_id: int
    content: str
    score: float


def reciprocal_rank_fusion(
    ranked_lists: List[List[Dict]],
    k: int = 60,
) -> List[FusedResult]:
    """
    score(doc) = sum over lists of 1 / (k + rank_int_that_list)
    k = 60 is the standard default from the original RRF paper, it dampens
    how much a single list's #1 spot can dominate the fused ranking.
    so one strong vector git can't drown out a strong keyword hit that ranks lower within its own list and vice versa.
    """
    scores: Dict[int, float] = {}
    content_by_id: Dict[int, str] = {}

    if k <= 0:
        raise ValueError("k must be greater than 0")

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, start=1):
            chunk_id = item["chunk_id"]
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
            content_by_id[chunk_id] = item["content"]

    fused = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)

    return [
        FusedResult(chunk_id=chunk_id, content=content_by_id[chunk_id], score=score)
        for chunk_id, score in fused
    ]
