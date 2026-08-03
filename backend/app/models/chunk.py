# backend/app/models/chunk.py
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Computed, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .document import Document
    from .message_citation import MessageCitation


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    # Points back into ChromaDB — this column is what links the two stores.
    embedding_id: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, index=True
    )

    # Postgres computes this automatically from `content` on every insert/update
    # the ORM never sends a value for it, so there's no way for it to drift out
    # of sync with the actual text. Nothing to set from Python, ever.
    tsv: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', content)", persisted=True),
        nullable=False,
    )

    document: Mapped["Document"] = relationship(back_populates="chunks")
    citations: Mapped[List["MessageCitation"]] = relationship(
        back_populates="chunk", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_chunks_tsv", "tsv", postgresql_using="gin"),
        Index(
            "ix_chunks_document_id_chunk_index",
            "document_id",
            "chunk_index",
            unique=True,
        ),
    )
