# backend/app/models/ticket.py

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import MessageRole

if TYPE_CHECKING:
    from .conversation import Conversation
    from .message_citation import MessageCitation


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[MessageRole] = mapped_column(
        SAEnum(MessageRole, name="message_role"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # raw LangGraph/LangChain tool call payload: kept as JSONB rather than a separate normalized table
    # since its shape depends on the tool ran.
    tool_calls: Mapped[Optional[dict]] = mapped_column(JSONB)
    prompt_tokens: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    citations: Mapped[List["MessageCitation"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )
