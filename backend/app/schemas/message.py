# backend/app/schemas/user.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import MessageRole


class MessageBase(BaseModel):
    role: MessageRole
    content: str


class MessageCreate(MessageBase):
    conversation_id: int
    tool_calls: dict | None = None
    prompt_tokens: int | None = None


class MessageRead(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    tool_calls: dict | None = None
    prompt_tokens: int | None = None
    created_at: datetime
