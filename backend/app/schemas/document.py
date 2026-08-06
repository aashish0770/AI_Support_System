# backend/app/schemas/document.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import DocumentStatus, DocumentSourceType


class DocumentBase(BaseModel):
    title: str
    source_type: DocumentSourceType


class DocumentCreate(DocumentBase):
    content_hash: str
    uploaded_by_user_id: int | None = None


class DocumentRead(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_hash: str
    status: DocumentStatus
    ingested_at: datetime
    uploaded_by_user_id: int | None = None
