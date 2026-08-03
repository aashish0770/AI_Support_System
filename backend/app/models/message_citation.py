# backend/app/models/message_citation.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .chunk import Chunk
    from .message import Message


class MessageCitation(Base):
    """Join entity, which chunks grounded a given assistant message,
    and how relevent each one was.
    this makes an answer traceable back to source.
    """

    __tablename__ = "message_citations"

    id: Mapped[int] = mapped_column(primry_key=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )
    chunk_id: Mapped[int] = mapped_column(
        ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False
    )
    relevence_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    message: Mapped["Message"] = relationship(back_populates="citations")
    chunk: Mapped["Chunk"] = relationship(back_populates="citations")
