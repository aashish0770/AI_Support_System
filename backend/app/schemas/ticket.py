# backend/app/schemas/user.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import TicketStatus


class TicketBase(BaseModel):
    subject: str
    description: str


class TicketCreate(TicketBase):
    pass


class TicketRead(TicketBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: TicketStatus
    created_at: datetime
