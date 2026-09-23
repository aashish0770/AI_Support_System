# backend/app/schemas/chat.py
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class CitationOut(BaseModel):
    chunk_id: int
    document_title: str
    relevance_score: float


class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationOut]
    # these 2 has been used in previous versions but not any more
    '''
    in_scope: bool = True
    suggested_topics: List[str] = []
    '''
