# backend/app/schemas/chunk.py
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ChunkBase(BaseModel):
    document_id: int
    chunk_index: int
    content: str
    metadata: dict | None = None


class ChunkCreate(ChunkBase):
    embedding_id: str | None = None
    # tsv is deliberately not settable via the API:
    # It's derived from `content` server-side


class ChunkRead(ChunkBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    embedding_id: str | None = None
    # tsv excluded, internal search artifact, not something a client needs.
