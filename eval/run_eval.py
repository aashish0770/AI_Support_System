"""
Retrieval evaluation harness.

Metrics:
    precision@k = (# retrieved chunks in top-k whose document is relevant) / k
    recall@k = (# distinct relevant doucments represented in top-k) / (# relevant documents for this query)

Run from the repo root:
    python eval/run_eval.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.db.session import get_session  # noqa: E402
from app.models.chunk import Chunk  # noqa: E402
from app.models.document import Document  # noqa: E402
from app.services.retrieval.hybrid_search import hybrid_search  # noqa: E402
from app.services.retrieval.keyword_search import keyword_search  # noqa: E402
from app.services.retrieval.vector_search import vector_search  # noqa: E402

TOP_K = 5
GOLDEN_DATASET_PATH = Path(__file__).resolve().parent / "golden_dataset.json"
RESULTS_PATH = Path(__file__).resolve().parent / "results.json"


def load_golden_dataset() -> List[Dict]:
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_chunk_id_to_title_map(db) -> Dict[int, str]:
    rows = db.execute(
        select(Chunk.id, Document.title).join(
            Document, Chunk.document_id == Document.id
        )
    ).all()
    return {chunk_id: title for chunk_id, title in rows}


def precision_recall_at_k(
    retrieved_chunk_ids: List[int],
    chunk_id_to_title: Dict[int, str],
    relevant_titles: Set[str],
    k: int,
) -> Tuple[float, float]:
    top_k_ids = retrieved_chunk_ids[:k]
    retrieved_titles = [chunk_id_to_title.get(cid) for cid in top_k_ids]

    relevant_hits = sum(1 for title in retrieved_titles if title in relevant_titles)
    precision = relevant_hits / k if k else 0.0

    distinct_relevant_retrieved = {t for t in retrieved_titles if t in relevant_titles}
    recall = (
        len(distinct_relevant_retrieved) / len(relevant_titles)
        if relevant_titles
        else 0.0
    )

    return precision, recall


def evaluate_method(method_name, search_fn, golden_dataset, chunk_id_to_title, db=None):
    precision, recalls, per_query = [], [], []

    for item in golden_dataset:
        query = item["query"]
        relevant_titles = set(item["relevant_titles"])

        results = (
            search_fn(db, query, top_k=TOP_K)
            if db is not None
            else search_fn(query, top_k=TOP_K)
        )
        retrieved_ids = [r["chunk_id"] for r in results]

        p, r = precision_recall_at_k(
            retrieved_ids, chunk_id_to_title, relevant_titles, TOP_K
        )
        precision.append(p)
        recalls.append(r)
        per_query.append({"query": query, "precision": p, "recall": r})

    return {
        "method": method_name,
        "mean_precision_at_k": sum(precision) / len(precision),
        "mean_recall_at_k": sum(recalls) / len(recalls),
        "per_query": per_query,
    }


def main():
    db = get_session()
    golden_dataset = load_golden_dataset()
    chunk_id_to_title = build_chunk_id_to_title_map(db)

    results = [
        evaluate_method(
            "vector-only", vector_search, golden_dataset, chunk_id_to_title
        ),
        evaluate_method(
            "keyword-only", keyword_search, golden_dataset, chunk_id_to_title, db=db
        ),
        evaluate_method(
            "hybrid", hybrid_search, golden_dataset, chunk_id_to_title, db=db
        ),
    ]

    print(f"{'Method':<15}{'Precision@'+ str(TOP_K):<15}{'Recall@'+ str(TOP_K):<15}")
    for r in results:
        print(
            f"{r['method']:<15}{r['mean_precision_at_k']:<15.3f}{r['mean_recall_at_k']:<15.3f}"
        )

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nFull per-query results written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
