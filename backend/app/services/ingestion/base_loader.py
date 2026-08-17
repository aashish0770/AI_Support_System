from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.enums import DocumentSourceType, DocumentStatus


class BaseLoader:
    # Subclasses must override this. Typed Optional rather than a bare
    # `None` annotation so the intent (must-override, not "always None") is
    # actually expressed in the type.
    source_type: Optional[DocumentSourceType] = None

    def compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def extract_title(self, text: str, fallback: str) -> str:
        for line in text.splitlines():
            clean = line.strip()
            if clean:
                return clean[:200]
        return fallback

    def _document_model(self):
        # Local import avoids a circular import between the ingestion
        # services and the models package at module load time.
        from app.models.document import Document as _Document

        return _Document

    def create_document_with_chunks(
        self,
        db: Session,
        *,
        title: str,
        content: str,
        content_hash: str,
        chunks: List[Dict[str, Any]],
        uploaded_by_user_id: int | None = None,
    ) -> Document:
        document = Document(
            title=title,
            source_type=self.source_type,
            content_hash=content_hash,
            status=DocumentStatus.pending,
            uploaded_by_user_id=uploaded_by_user_id,
        )

        try:
            db.add(document)
            db.flush()  # assigns document.id without committing yet

            db.add_all(
                [
                    Chunk(
                        document_id=document.id,
                        chunk_index=chunk["chunk_index"],
                        content=chunk["content"],
                        metadata_json=chunk.get("metadata") or None,
                        # embedding_id intentionally left NULL here — it's
                        # populated in Week 3 once this chunk's vector is
                        # written to ChromaDB. Document.status also stays
                        # "pending" for the same reason: a document isn't
                        # retrieval-ready until its chunks have embeddings,
                        # and marking it "processed" here would let
                        # vector-search code assume readiness that
                        # doesn't exist yet.
                    )
                    for chunk in chunks
                ]
            )

            db.commit()
            db.refresh(document)
        except Exception:
            db.rollback()
            raise

        return document