# ADR-0002: Hybrid retrieval (Postgres full-text + vector) over vector-only or Elasticsearch

## Status
Accepted

## Context
Retrieval quality is the core value proposition of the whole system — a support assistant that can't reliably find the right document is not a useful assistant. Pure vector (embedding) search is the default approach in most RAG tutorials, but embedding similarity tends to blur exact matches: precise terms like ticket IDs, error codes, and product names are often better served by literal keyword matching than by semantic similarity, which can retrieve conceptually-related-but-wrong results for these queries.

## Decision
Run two retrieval strategies in parallel and merge results via Reciprocal Rank Fusion (RRF):
- **Keyword search** via PostgreSQL's built-in `tsvector`/`ts_rank`, using a `GENERATED ALWAYS AS` column on `chunks.content` so the search index can never drift out of sync with the source text.
- **Semantic search** via ChromaDB, using local embeddings (`sentence-transformers/all-MiniLM-L6-v2`).

Both are queried on every retrieval-requiring turn; RRF combines the two ranked lists into one.

## Alternatives considered
- **Vector-only retrieval** — simpler to implement and reason about, but weak on exact-term queries (ticket numbers, specific error codes) which are common in a support context.
- **Elasticsearch for keyword search** — the more "industry standard" choice for full-text search at scale, but it's a separate service to run, configure, and keep in sync with Postgres, for a corpus far smaller than what would justify that operational overhead. Postgres `tsvector` covers the same need at this project's scale without adding infrastructure.

## Consequences
- Two retrieval paths to maintain and reason about instead of one, and RRF's fusion behavior is itself a design choice worth being able to explain (it favors items that rank reasonably well in *both* lists over an item that's #1 in one list and absent from the other).
- The eval harness (see ADR context in `eval/`) is what actually proves whether hybrid retrieval outperforms vector-only for this corpus, rather than assuming it does — retrieval quality claims are backed by a comparison, not asserted.
- Ties directly to the decision to use a Postgres `Computed` column for `tsv` rather than populating it from application code (see the schema/model implementation) — this was chosen specifically so the keyword index can never fall out of sync with edited content.