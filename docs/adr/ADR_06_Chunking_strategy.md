# ADR-0006: Chunking strategy

## Status

Accepted

## Context

Chunks need to be small enough for embeddings to capture focused meaning, and large enough to retain useful context. The chunking approach also directly affects retrieval quality, which the eval harness (Week 5) will measure.

## Decision

Fixed-size recursive character splitting via LangChain's `RecursiveCharacterTextSplitter`, sized by **token count** (500 tokens, 50 token overlap) rather than raw character count, using `tiktoken`'s `cl100k_base` encoding as the length function.

Token-based sizing was chosen deliberately over character-based sizing even though the project doesn't use an OpenAI model for generation — `cl100k_base` is a free, local, reasonably-representative proxy for how token-dense different content is. Code blocks, JSON snippets, and prose tokenize very differently per character, so a character-based `chunk_size=500` would produce wildly inconsistent actual token counts across the corpus, while a token-based one keeps chunk sizes consistent in the unit that actually matters for embedding model input limits.

## Alternatives considered

- **Character-based sizing** — simpler, no `tiktoken` dependency, but produces inconsistent effective chunk sizes across code-heavy vs. prose-heavy documents (see Context).
- **Semantic chunking** (splitting on meaning boundaries via an embedding-similarity-based splitter) — a stronger approach in principle, but adds real complexity and its own cost (extra embedding calls just to decide where to split). Deferred as a stretch goal explicitly measurable against fixed-size splitting via the Week 5 eval harness — if precision/recall don't improve enough to justify the complexity, fixed-size stays.

## Consequences

- Chunk boundaries can land mid-thought for prose content — accepted as a known tradeoff of fixed-size splitting.
- The 50-token overlap is what limits complete loss of context at chunk boundaries; not eliminated, mitigated.
- This decision is explicitly revisitable and testable, not fixed permanently — the eval harness built in Week 5 is what will make "was this the right call" an evidence-based answer rather than an assumption.
