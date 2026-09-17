"""Compare vector-only, keyword-only, and hybrid retrieval
side by side on the same query set used in previous spot-check. Not the
formal eval harness: this is what that harness will later make
rigorous with real precision@k numbers instead of eyeballing."""

from __future__ import annotations

from app.db.session import get_session
from app.services.retrieval.hybrid_search import hybrid_search
from app.services.retrieval.keyword_search import keyword_search
from app.services.retrieval.vector_search import vector_search
from scripts.spot_check import QUERIES


def _preview(text: str, length: int = 90) -> str:
    return text[:length].replace("\n", " ")


def main() -> None:
    db = get_session()

    for query in QUERIES:
        print("=" * 90)
        print(f"QUERY: {query}")

        print("  [vector]")
        for r in vector_search(query, top_k=3):
            print(f"    dist={r['distance']:.3f}  {_preview(r['content'])}")

        print("  [keyword]")
        kw_results = keyword_search(db, query, top_k=3)
        if not kw_results:
            print("    (no matches)")
        for r in kw_results:
            print(f"    rank={r['rank']:.3f}  {_preview(r['content'])}")

        print("  [hybrid]")
        for r in hybrid_search(db, query, top_k=3):
            print(f"    score={r['score']:.4f}  {_preview(r['content'])}")


if __name__ == "__main__":
    main()
