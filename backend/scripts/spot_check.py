""" manual retrieval spot-check.

Not the formal eval harness (that's in upcomming process) — this prints results for a
fixed query set so they can be eyeballed and recorded. The query list
here becomes the seed for next time golden dataset.
"""

from __future__ import annotations

from app.services.retrieval.vector_search import vector_search

QUERIES = [
    # Conceptual — vector search should handle these well
    "how do I verify a webhook signature",
    "what happens if I exceed my rate limit",
    "how do I connect Slack to my account",
    "can I get data back after deleting my account",
    "why is my workflow not triggering for existing rows",
    "how do I set up single sign-on",
    "what happens when I downgrade my plan",
    "how do I stop duplicate messages being sent",
    # Exact-term — vector search is expected to struggle here.
    # These are the cases for next time upgrade keyword search exists to rescue.
    "AUTH_KEY_REVOKED",
    "wf_9f2a1c",
    "clk_live_",
    "channel_not_found",
    "Cobalt-Signature",
    "429",
    "SCIM",
]


def main() -> None:
    for query in QUERIES:
        print("=" * 80)
        print(f"QUERY: {query}")
        results = vector_search(query, top_k=3)
        if not results:
            print("  (no results)")
            continue
        for rank, result in enumerate(results, start=1):
            preview = result["content"][:100].replace("\n", " ")
            print(f"  {rank}. [dist={result['distance']:.3f}] {preview}")


if __name__ == "__main__":
    main()
