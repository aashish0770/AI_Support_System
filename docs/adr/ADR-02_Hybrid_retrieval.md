# ADR-0002: Hybrid retrieval (Postgres full-text + vector) over vector-only or Elasticsearch

## Status
Accepted

## Context
Retrieval quality is the core value proposition of the whole system -- a support assistant that can't reliably find the right document is not a useful assistant. Pure vector (embedding) search is the default approach in most RAG tutorials, but embedding similarity tends to blur exact matches: precise terms like ticket IDs, error codes, and product names are often better served by literal keyword matching than by semantic similarity, which can retrieve conceptually-related-but-wrong results for these queries.

## Decision
Run two retrieval strategies in parallel and merge results via Reciprocal Rank Fusion (RRF):
- **Keyword search** via PostgreSQL's built-in `tsvector`/`ts_rank`, using a `GENERATED ALWAYS AS` column on `chunks.content` so the search index can never drift out of sync with the source text.
- **Semantic search** via ChromaDB, using local embeddings (`sentence-transformers/all-MiniLM-L6-v2`).

Both are queried on every retrieval-requiring turn; RRF combines the two ranked lists into one.

## Alternatives considered
- **Vector-only retrieval** -- simpler to implement and reason about, but weak on exact-term queries (ticket numbers, specific error codes) which are common in a support context.
- **Elasticsearch for keyword search** -- the more "industry standard" choice for full-text search at scale, but it's a separate service to run, configure, and keep in sync with Postgres, for a corpus far smaller than what would justify that operational overhead. Postgres `tsvector` covers the same need at this project's scale without adding infrastructure.

## Consequences
- Two retrieval paths to maintain and reason about instead of one, and RRF's fusion behavior is itself a design choice worth being able to explain (it favors items that rank reasonably well in *both* lists over an item that's #1 in one list and absent from the other).
- The eval harness (see ADR context in `eval/`) is what actually proves whether hybrid retrieval outperforms vector-only for this corpus, rather than assuming it does - retrieval quality claims are backed by a comparison, not asserted.
- Ties directly to the decision to use a Postgres `Computed` column for `tsv` rather than populating it from application code (see the schema/model implementation) - this was chosen specifically so the keyword index can never fall out of sync with edited content.

## Results (added after comparison)

Verified against the spot-check query set (full output: `eval/comparison-raw.txt`).

- **"what happens if I exceed my rate limit"** -- vector-only ranked "Billing & Plans" (dist=0.538) above "Rate Limits" (dist=0.558) -- the two chunks are conceptually close enough that embedding similarity alone couldn't cleanly separate them. Keyword search correctly identified "Rate Limits" as the strongest exact-term match. Hybrid fusion corrected the ordering, surfacing "Rate Limits" first -- a genuine case of hybrid fixing a vector-only near-miss, not just confirming what vector already got right.

- **"how do I verify a webhook signature"** -- vector-only already ranked the correct "Webhooks" doc chunk first (dist=0.318). Keyword search agreed. Hybrid fusion preserved this ranking. Worth noting honestly: this query didn't need hybrid to succeed - it's included to show hybrid doesn't regress cases vector-only already handles well.

- **"AUTH_KEY_REVOKED"** (from Day 1/3 checkpoints) -- neither vector-only nor keyword-only alone put the single best-matching chunk unambiguously at #1; RRF fusion correctly surfaced both the ticket resolution and the doc's error-code table at a tied top rank, since each ranked #1 in one list and #2 in the other.

Takeaway: hybrid retrieval doesn't uniformly outperform vector-only on every query - on queries vector-only already handles well, it preserves that result. Its value shows specifically on exact-term and near-miss cases, which is exactly the class of query it was chosen to address (see Context above). The Week 5 evaluation harness formalizes this into precision@k/recall@k numbers across a full query set, rather than relying on spot-checked examples alone.