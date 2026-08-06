# ADR-0004: Redis for caching and rate limiting over in-process alternatives

## Status
Accepted

## Context
Two cross-cutting concerns need a shared store: caching repeated LLM/retrieval results to avoid redundant work, and rate limiting requests per user/IP. Both could be implemented in-process (e.g. `diskcache` for caching, an in-memory counter for rate limiting), which would avoid running an extra service.

## Decision
Use Redis, run as its own container in `docker-compose.yml`, for both response caching and rate limiting (via `slowapi`).

## Alternatives considered
- **`diskcache` (file-based cache)** — zero additional infrastructure, works out of the box. Rejected specifically because it's a materially weaker answer to "why not Redis?" in an interview setting — file-based caching doesn't survive a multi-process deployment (each worker process would have its own cache), and Redis is free to self-host, so there's no real cost tradeoff being avoided by choosing the simpler option.
- **In-memory rate limiting** (e.g. a plain Python dict with timestamps) — works for a single process, but breaks the moment the backend runs as more than one worker, since each process would track its own independent counters. Redis-backed rate limiting is correct regardless of process count.

## Consequences
- One more service in `docker-compose.yml`, but it's a lightweight, well-understood addition with a documented healthcheck.
- Cache keys are built from normalized query + retrieved chunk hash rather than raw query strings, so cache invalidation behaves predictably when underlying chunks change — this is a deliberate design detail worth being able to explain, not an incidental implementation choice.
- Sets up Redis as available infrastructure for future features beyond its initial two uses (e.g. session storage, pub/sub for streaming coordination), without needing to introduce a new service later.