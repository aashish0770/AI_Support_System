# backend/app/services/ingestion/ticket_loader.py
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger
from sqlalchemy.orm import Session

from app.models.enums import DocumentSourceType
from app.services.ingestion.base_loader import BaseLoader
from app.services.ingestion.chunker import split_text

# Same fix as markdown_loader.py — anchored to this file's location, not
# the caller's working directory, so it resolves correctly whether run
# from the repo root on the host or from /app inside the container.
TICKET_PATH = Path(__file__).resolve().parents[3] / "data" / "raw" / "tickets"


class TicketLoader(BaseLoader):
    source_type = DocumentSourceType.ticket

    # -- file readers --
    def _read_json(self, file_path: Path) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _read_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    # -- normalization --
    def _normalize_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a raw ticket record into a consistent content + metadata shape."""
        # `(value or "")` rather than `.get(key, "")` — this guards against
        # a key existing with an explicit null value, not just a missing
        # key. dict.get's default only applies when the key is absent.
        subject = (ticket.get("subject") or "").strip()
        description = (ticket.get("description") or "").strip()
        resolution = (ticket.get("resolution_notes") or "").strip()

        content = f"""
Subject: {subject}

Description:
{description}

Resolution:
{resolution}
""".strip()

        metadata = {
            "status": ticket.get("status"),
            "priority": ticket.get("priority"),
            "created_at": ticket.get("created_at"),
        }

        return {
            "title": subject or "Untitled Ticket",
            "content": content,
            "metadata": metadata,
        }

    # -- ingest --
    def ingest(self, db: Session, uploaded_by_user_id: int | None = None) -> int:
        ingested_count = 0
        files = sorted(TICKET_PATH.glob("*"))

        for file_path in files:
            if file_path.suffix == ".json":
                tickets = self._read_json(file_path)
            elif file_path.suffix == ".csv":
                tickets = self._read_csv(file_path)
            else:
                continue

            for ticket in tickets:
                normalized = self._normalize_ticket(ticket)
                content = normalized["content"]
                title = normalized["title"]
                metadata = normalized["metadata"]

                content_hash = self.compute_hash(content)

                existing = (
                    db.query(self._document_model())
                    .filter_by(content_hash=content_hash)
                    .first()
                )
                if existing:
                    continue

                chunks = split_text(
                    content,
                    extra_metadata={"source_type": self.source_type.value, **metadata},
                )

                self.create_document_with_chunks(
                    db,
                    title=title,
                    content=content,
                    content_hash=content_hash,
                    chunks=chunks,
                    uploaded_by_user_id=uploaded_by_user_id,
                )
                ingested_count += 1
                logger.info(f"Ticket ingested: {title}")

        return ingested_count
