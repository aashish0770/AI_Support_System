"""Ingestion loaders, keyed by source type.

Registering every loader here — including ones not yet wired into a CLI
command — is the real fix for static analysis tools (SonarQube,
CodeRabbit) flagging a loader class as unused/dead code. A comment saying
"this is used, I promise" doesn't change what the analyzer sees; an actual
reference does. PDFLoader isn't called by ingest.py yet, but it's
referenced right here, so it's genuinely in use by the registry even
before a PDF source exists in the data.
"""

from app.models.enums import DocumentSourceType
from app.services.ingestion.markdown_loader import MarkdownLoader
from app.services.ingestion.pdf_loader import PDFLoader
from app.services.ingestion.ticket_loader import TicketLoader

LOADER_REGISTRY = {
    DocumentSourceType.markdown: MarkdownLoader,
    DocumentSourceType.pdf: PDFLoader,
    DocumentSourceType.ticket: TicketLoader,
}

__all__ = ["MarkdownLoader", "PDFLoader", "TicketLoader", "LOADER_REGISTRY"]
