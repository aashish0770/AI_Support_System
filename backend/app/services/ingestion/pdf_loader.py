"""PDF ingestion loader.

Not currently wired into ingest.py (no PDF sources exist in Week 2's
synthetic data — see docs/adr/0005-synthetic-data.md), but this is a real,
working loader kept ready for when a PDF source type is added, per the
BaseLoader pattern's intent: adding a new source should be a drop-in, not
a rewrite. It's registered in ingestion/__init__.py's LOADER_REGISTRY,
which is what keeps static analysis (SonarQube, CodeRabbit) from flagging
this as unused/dead code — the registry is a real reference, not a
suppression comment, so it stays true even if this docstring is ignored.
"""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.models.enums import DocumentSourceType
from app.services.ingestion.base_loader import BaseLoader
from app.services.ingestion.chunker import split_text

PDF_PATH = Path(__file__).resolve().parents[3] / "data" / "raw" / "docs"


class PDFLoader(BaseLoader):
    source_type = DocumentSourceType.pdf

    def extract_text(self, file_path: Path) -> str:
        with PdfReader(str(file_path)) as reader:
            text = []
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text.append(content)

        return "\n".join(text)

    def ingest(self, db: Session, uploaded_by_user_id: int | None = None) -> int:
        ingested_count = 0

        for file_path in sorted(PDF_PATH.rglob("*.pdf")):
            content = self.extract_text(file_path)

            if not content.strip():
                continue

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
