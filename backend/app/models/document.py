# backend/app/models/document.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import DocumentSourceType, DocumentStatus

if TYPE_CHECKING:
    from .chunk import Chunk
    from .user import User


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    # a document should not vanish just because the user is deleted
    uploaded_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[DocumentSourceType] = mapped_column(
        SAEnum(DocumentSourceType, name="document_source_type"), nullable=False
    )
    # sha256 hex digest — this is what ingest.py checks before reprocessing.
    content_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus, name="document_status"),
        default=DocumentStatus.pending,
        nullable=False,
    )
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    uploaded_by: Mapped[Optional["User"]] = relationship(back_populates="documents")
    chunks: Mapped[List["Chunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="Chunk.chunk_index",
    )
