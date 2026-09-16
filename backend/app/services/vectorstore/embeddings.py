# backend/app/services/vectorstore/embeddings.py

from __future__ import annotations

from functools import lru_cache
from typing import List

from langchain_huggingface import HuggingFaceEmbeddings

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2's 384 dimensions output


@lru_cache
def get_embedding_model() -> HuggingFaceEmbeddings:
    """Cached so the model loads once per process, not once per request.

    1st call to this function will load the model into memory,
    subsequent calls will return the cached instance
    and use local HuggingFace cache
    """

    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        encode_kwargs={"normalize_embeddings": True},
    )


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Emded documents for indexing"""
    return get_embedding_model().embed_documents(texts)


def embed_query(text: str) -> List[float]:
    """Embed a query for searching the index

    Separate from embed_texts even though this model treats thm identically,
    because some embedding models use different prefixes for indexing vs. querying
    and keeping the split now means swapping model later is easier. and doesn't require hunting down every call site.
    """

    return get_embedding_model().embed_query(text)
