# ADR-0003: ChromaDB over pgvector or a managed vector database

## Status
Accepted

## Context
Semantic search needs a place to store and query embeddings efficiently. The project already runs PostgreSQL for relational data, which raises the question of whether a separate vector store is needed at all, versus extending Postgres itself.

## Decision
Use ChromaDB as a standalone vector store, run as its own service, with `chunks.embedding_id` in Postgres holding a reference back into Chroma rather than storing vectors in Postgres directly.

## Alternatives considered
- **`pgvector` extension** — would consolidate everything into one database, removing a service to run and one less place for data to get out of sync. Reasonable choice, but ChromaDB was picked instead specifically to demonstrate hands-on experience with a purpose-built vector database as a distinct component, which is closer to how larger-scale systems typically separate these concerns, and is common in the RAG tooling ecosystem this project is meant to demonstrate familiarity with.
- **A managed vector DB (Pinecone, Weaviate Cloud, etc.)** — removes operational overhead entirely, but introduces a paid external dependency and network latency for every query, which conflicts with the project's local-first, cost-free constraint (see ADR-0001).

## Consequences
- Two databases to keep logically in sync (a chunk's row in Postgres must have a matching vector in Chroma, linked by `embedding_id`) — this is exactly the failure mode addressed by the ingestion pipeline's ordering (create the `documents` row before requesting embeddings, so a mid-pipeline failure is traceable rather than producing orphaned vectors).
- Chroma runs embedded/local by default, so this doesn't add a meaningfully heavier operational footprint than `pgvector` would have, while still demonstrating the distinct-vector-store pattern.
- If corpus size or query volume ever became a genuine scaling concern, this is the component most likely to be revisited — worth noting as a known tradeoff rather than a permanent decision.