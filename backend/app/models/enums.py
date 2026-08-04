# backend/app/models/enums.py
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    customer = "customer"


class DocumentSourceType(str, enum.Enum):
    markdown = "markdown"
    tickets = "tickets"
    pdf = "pdf"


class DocumentStatus(str, enum.Enum):
    pending = "pending"
    processed = "processed"
    failed = "failed"


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    tool = "tool"
    system = "system"
