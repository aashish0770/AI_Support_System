from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

# parents[3] from this file (vectorstore -> services -> app -> backend)
# lands on the backend root, same CWD independence approach used by
# the ingestion loaders and alembic/env.py

CHROMA_DIR = Path(__file__).resolve().parents[3] / "chroma_data"

COLLECTION_NAME = "cobalt_loop_chunks"

_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR), settings=ChromaSettings(anonymized_telemetry=False)
)


def get_collection():
    """Single owner of the Chroma collection.

    NOTE: Chroma's PersistentClient takes a lock on its data directory.
    Because backend/ is bind-mounted into backend container, the host
    and the container point at the SAME chroma_data folder, so don't run
    the embed CLI on the host while the container is also touching Chroma.

    For Weeks 3-4 everything runs on the host, so this is fine; revisit
    when the FastAPI app starts querying Chroma in Week 6.
    """
    return _client.get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
