# backend/app/services/agent/tool_schemas.py

from __future__ import annotations

from typing import List, TypedDict


class DocExcerpt(TypedDict):
    chunk_id: int
    document_title: str
    content: str
    relevance_score: float


class SearchDocsResponse(TypedDict):
    found: bool
    results: List[DocExcerpt]
