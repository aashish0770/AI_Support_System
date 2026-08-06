# backend/app/schemas/message_citation.py

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MessageCitationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message_id: int
    chunk_id: int
    relevance_score: float
