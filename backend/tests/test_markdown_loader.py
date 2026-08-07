import pytest

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.enums import DocumentSourceType, DocumentStatus
from app.services.ingestion.markdown_loader import MarkdownLoader


@pytest.fixture()
def sample_docs_dir(tmp_path, monkeypatch):
    """Point the loader at a throwaway directory instead of the real
    backend/data/raw/docs, so tests don't depend on — or accidentally
    mutate assumptions about — the real synthetic dataset."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "sample.md").write_text(
        "# Sample Doc\n\n"
        "This is a short sample document used for testing the markdown "
        "loader's ingestion behavior. It has enough content to produce "
        "at least one real chunk.",
        encoding="utf-8",
    )

    import app.services.ingestion.markdown_loader as loader_module

    monkeypatch.setattr(loader_module, "DOCS_PATH", docs_dir)
    return docs_dir


def test_extract_title_uses_first_heading():
    loader = MarkdownLoader()
    text = "# My Real Title\n\nSome body text."

    assert loader.extract_title(text, fallback="fallback-name") == "My Real Title"


def test_extract_title_falls_back_when_no_heading():
    loader = MarkdownLoader()
    text = "No heading here, just a plain paragraph."

    assert loader.extract_title(text, fallback="fallback-name") == "fallback-name"


def test_ingest_creates_document_and_chunks(db_session, sample_docs_dir):
    loader = MarkdownLoader()

    ingested = loader.ingest(db_session)

    assert ingested == 1

    document = db_session.query(Document).filter_by(title="Sample Doc").one()
    assert document.source_type == DocumentSourceType.markdown
    # Deliberately still "pending" here — see base_loader.py's comment.
    # A document with chunks but no embeddings yet isn't retrieval-ready.
    assert document.status == DocumentStatus.pending

    chunks = db_session.query(Chunk).filter_by(document_id=document.id).all()
    assert len(chunks) >= 1
    assert all(chunk.embedding_id is None for chunk in chunks)
    assert all(isinstance(chunk.content, str) and chunk.content for chunk in chunks)
    # Metadata should have actually made it onto the chunk, not been
    # silently dropped (this was the original bug in create_document_with_chunks).
    assert chunks[0].metadata_json is not None
    assert chunks[0].metadata_json.get("source_type") == "markdown"


def test_ingest_is_idempotent(db_session, sample_docs_dir):
    loader = MarkdownLoader()

    first_run = loader.ingest(db_session)
    second_run = loader.ingest(db_session)

    assert first_run == 1
    assert second_run == 0  # same content_hash already exists, nothing new inserted

    documents = db_session.query(Document).all()
    assert len(documents) == 1


def test_ingest_skips_files_with_different_content_separately(
    db_session, sample_docs_dir
):
    """Two files with different content should both be ingested as
    separate documents, not deduplicated against each other."""
    (sample_docs_dir / "second.md").write_text(
        "# Second Doc\n\nCompletely different content from the first file.",
        encoding="utf-8",
    )

    loader = MarkdownLoader()
    ingested = loader.ingest(db_session)

    assert ingested == 2
    titles = {doc.title for doc in db_session.query(Document).all()}
    assert titles == {"Sample Doc", "Second Doc"}
