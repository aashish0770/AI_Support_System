# backend/app/models/message.py
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
    # Raw LangGraph/LangChain tool call payload — kept as JSONB rather than a
    # separate normalized table, since its shape depends on which tool ran.
    tool_calls: Mapped[Optional[dict]] = mapped_column(JSONB)
    # Nullable: not every message has a meaningful token count (e.g. system
    # or tool messages), and a fake 0 would be indistinguishable from a real
    # one later if build usage tracking.
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    citations: Mapped[List["MessageCitation"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )
