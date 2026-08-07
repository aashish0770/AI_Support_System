from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.models.enums import DocumentSourceType
from app.services.ingestion.base_loader import BaseLoader
from app.services.ingestion.chunker import split_text

# Resolved relative to this file's own location, not the process's current
# working directory. A hardcoded "backend/data/raw/docs" string resolves
# differently depending on whether this runs from the repo root on the host
# or from /app inside the backend container (where /app IS backend/, so the
# same string would double up and point nowhere). parents[3] from this file
# (ingestion -> services -> app -> backend) lands on "the backend directory"
# correctly in both environments.
DOCS_PATH = Path(__file__).resolve().parents[3] / "data" / "raw" / "docs"


class MarkdownLoader(BaseLoader):
    source_type = DocumentSourceType.markdown

    def extract_title(self, text: str, fallback: str) -> str:
        for line in text.splitlines():
            if line.startswith("#"):
                return line.lstrip("#").strip()
        return super().extract_title(text, fallback)

    def ingest(self, db: Session, uploaded_by_user_id: int | None = None) -> int:
        """Ingest every .md file under DOCS_PATH. Returns the count of
        newly-ingested documents (skips ones already seen via content_hash)."""
        ingested_count = 0

        for file_path in sorted(DOCS_PATH.rglob("*.md")):
            content = file_path.read_text(encoding="utf-8")
            content_hash = self.compute_hash(content)

            existing = (
                db.query(self._document_model())
                .filter_by(content_hash=content_hash)
                .first()
            )
            if existing:
                continue

            title = self.extract_title(content, file_path.stem)
            chunks = split_text(
                content,
                extra_metadata={
                    "source_type": self.source_type.value,
                    "source_filename": file_path.name,
                },
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

        return ingested_count
