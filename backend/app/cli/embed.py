# backend/app/cli/embed.py

from __future__ import annotations

from typing import List

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.enums import DocumentStatus
from app.services.vectorstore.chroma_client import get_collection
from app.services.vectorstore.embeddings import embed_texts

# Embedding and writing in batches rather then all at once keeps memory bounded
# and gives partial progress if something goes wrong or fails midway.
# 64 is a reasonable chunk size for CUP-only sentence transformers model.
BATCH_SIZE = 64


def _embed_batch(db: Session, collection, chunks: List[Chunk]) -> int:
    contents = [chunk.content for chunk in chunks]
    vectors = embed_texts(contents)

    # upsert, not added to avoid add() error on duplicate embedding_id
    # which would make a partial-failure retry impossible. upser makes re-running safe even
    # if Postgres rolled back after Chroma already accepted the write.
    collection.upsert(
        ids=[f"chunk_{chunk.id}" for chunk in chunks],
        embeddings=vectors,
        documents=contents,
        metadatas=[
            {"document_id": chunk.document_id, "chunk_id": chunk.id} for chunk in chunks
        ],
    )

    for chunk in chunks:
        chunk.embedding_id = f"chunk_{chunk.id}"

    db.commit()
    return len(chunks)


def _promote_fully_embedded_documents(db: Session) -> int:
    """Flip documents to `processed` once every one of their chunks has an embedding.
    this is a deferred hald of the ordering decided in ADR_o2:
    a document isn't retrieval-ready until its vectors exists.
    """
    pending_docs = (
        db.execute(select(Document).where(Document.status == DocumentStatus.pending))
        .scalars()
        .all()
    )

    promoted = 0
    for document in pending_docs:
        if document.chunks and all(c.embedding_id is not None for c in document.chunks):
            document.status = DocumentStatus.processed
            promoted += 1

    db.commit()
    return promoted


def embed_pending_chunks() -> int:
    db = get_session()
    collection = get_collection()
    embedded_total = 0

    try:
        pending_chunks = (
            db.execute(
                select(Chunk).where(Chunk.embedding_id.is_(None)).order_by(Chunk.id)
            )
            .scalars()
            .all()
        )

        if not pending_chunks:
            logger.info("No pending chunks to embed.")
        else:
            logger.info(f"found {len(pending_chunks)} chunk(s) pending embedding")

            for start in range(0, len(pending_chunks), BATCH_SIZE):
                batch = pending_chunks[start : start + BATCH_SIZE]
                embedded_total += _embed_batch(db, collection, batch)
                logger.info(
                    f"Embedded {embedded_total}/{len(pending_chunks)} chunk(s)."
                )

        promoted = _promote_fully_embedded_documents(db)
        logger.info(f"Promoted {promoted} document(s) to processed status.")
        return embedded_total
    except Exception:
        db.rollback()
        logger.exception(
            "Error occurred during embedding process. Rolling back changes."
        )
        raise
    finally:
        db.close()


if __name__ == "__main__":
    embed_pending_chunks()
