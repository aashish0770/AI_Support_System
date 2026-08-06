# ADR-0005: Synthetic data, and how it's kept honest

## Status
Accepted

## Context
This is a portfolio project, not a system built for a real company — there is no real enterprise document corpus, real ticket history, or real user base to ingest. The system still needs realistic-enough data to demonstrate ingestion, retrieval, and agent behavior meaningfully, and any ambiguity about whether the data is real could undermine trust in the project if discovered rather than disclosed.

## Decision
Generate synthetic data for a fictional company, **Northbridge Cloud** (a B2B SaaS providing API infrastructure tooling — auth, webhooks, data pipelines), consisting of:
- 8–12 markdown "product docs" (setup guides, API references, troubleshooting pages)
- 15–20 synthetic support tickets (subject, description, status, priority, resolution notes) in JSON/CSV

This is stated explicitly and prominently — in this ADR, in the README, and in code comments near the data generation — rather than left ambiguous. AI assistance was used to draft the synthetic content itself, which is a legitimate and disclosed use given the content is explicitly fictional and not presented as real.

## Alternatives considered
- **Scraping real public documentation** (e.g. an open-source project's docs) — would be "real" data, but introduces licensing/attribution questions and doesn't naturally include the ticket-style data needed to demonstrate the tool-calling agent path (`check_ticket_status`).
- **Leaving data provenance unstated** — the simplest option, but the wrong one: an interviewer or reviewer discovering the data is fake without it being disclosed reads as either sloppy or evasive. Stating it upfront costs nothing and prevents that entirely.

## Consequences
- Retrieval quality results (from the eval harness) are only as meaningful as the synthetic corpus's realism — worth being upfront in any discussion of eval numbers that they're measured against synthetic, not production, data.
- The fictional company name, once chosen, should be used consistently across the docs, tickets, and any UI copy, so the demo reads as one coherent system rather than a patchwork of disconnected sample data.