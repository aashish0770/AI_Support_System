# backend/app/core/config.py

from __future__ import annotations

import argparse
import sys

from loguru import logger

from app.db.session import get_session
from app.models.enums import DocumentSourceType
from app.services.ingestion import LOADER_REGISTRY

# This dict is one deliberate place that translates between
# the CLI source name and the document source type.
CLI_SOURCE_MAP = {
    "docs": DocumentSourceType.markdown,
    "tickets": DocumentSourceType.ticket,
    "pdf": DocumentSourceType.pdf,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest raw source data into the RAG pipeline."
    )
    
    parser.add_argument(
        "--source",
        required=True,
        choices=sorted(CLI_SOURCE_MAP.keys()),
        help="Which source type to ingest.",
    )
    
    args = parser.parse_args()

    source_type = CLI_SOURCE_MAP[args.source]
    loader_cls = LOADER_REGISTRY[source_type]

    if loader_cls is None:
        logger.error(f"No loader registered for source type '{args.source}'.")
        sys.exit(1)

    loader = loader_cls()
    db = get_session()

    try:
        count = loader.ingest(db)
        logger.info(f"Ingested {count} new document(s) for source '{args.source}'.")
    except Exception:
        logger.exception(f"Ingestion failed for source '{args.source}'.")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
