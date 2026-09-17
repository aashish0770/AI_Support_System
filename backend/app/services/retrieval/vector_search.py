# backend/app/services/retrieval/vector_search.py

from __future__ import annotations

from typing import List, TypedDict

from app.services.vectorstore.chroma_client import get_collection
from app.services.vectorstore.embeddings import embed_query


class VectorSearchResult(TypedDict):
    chunk_id: int
    content: str
    distance: float


def vector_search(query: str, top_k: int = 5) -> List[VectorSearchResult]:
    if not 1 <= top_k <= 50:
        raise ValueError("top_k must be between 1 and 50")

    collection = get_collection()
    query_vector = embed_query(query)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    # Chroma returns a list-per-query, we only send one query,
    # so index[0]. An empty collection returns empty inner lists rather than raising,
    # do guard instead of letting zip() silently on-op.
    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    if not documents:
        return []

    return [
        VectorSearchResult(
            chunk_id=int(metadata["chunk_id"]),
            content=document,
            distance=distance,
        )
        for document, metadata, distance in zip(documents, metadatas, distances)
    ]
