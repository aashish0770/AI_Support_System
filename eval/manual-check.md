# Week 4 Day 4 — Vector Retrieval Spot-Check Baseline

## Purpose

This document records the exact retrieval results produced by the manual retrieval spot-check.

**Important:** These results are the baseline for **Week 4 Day 4** comparison and should be kept unchanged so that future retrieval changes can be compared against the same query set.

The query set will also become the seed for the **Week 5 formal evaluation / golden dataset harness**.

---

## Script

The spot-check uses a fixed query set and calls:

```python
results = vector_search(query, top_k=3)
```

The query list is intentionally split into:

- **Conceptual queries** — vector search should handle these well.
- **Exact-term queries** — vector-only search is expected to be weaker; these become useful cases when keyword/hybrid search is added.

---

# Baseline Results

The following output is the exact result set from the current vector-only retrieval implementation.

## Conceptual Queries

### 1. `how do I verify a webhook signature`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.318 | `# Webhooks` — Webhooks let Cobalt Loop notify your own server when a workflow event happens... |
| 2 | 0.364 | `Subject: Webhook signature verification always fails` — Our HMAC-SHA256... |
| 3 | 0.534 | `Subject: Webhook marked Failed after exactly 4 retries, is that expected?` — Our endpoint... |

### 2. `what happens if I exceed my rate limit`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.538 | `# Billing & Plans` — Plan comparison... |
| 2 | 0.558 | `# Rate Limits` — Cobalt Loop enforces rate limits per API key... |
| 3 | 0.631 | `Subject: Monthly task limit exceeded — will our workflows stop running?`... |

### 3. `how do I connect Slack to my account`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.402 | `Subject: Slack action failing with channel_not_found` — Our SendMessage action... |
| 2 | 0.413 | `# Slack Integration` — Connecting Slack: Settings → Connected Apps → Slack → Connect... |
| 3 | 0.511 | `# API Reference: Triggers & Actions` — Listing available trigger/action apps... |

### 4. `can I get data back after deleting my account`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.665 | `Subject: Export of run history for compliance before account deletion`... |
| 2 | 0.689 | `# Data Retention Policy` — Workflow run history... |
| 3 | 0.758 | `Subject: Can we get retroactive processing for rows added before the workflow was turned on?`... |

### 5. `why is my workflow not triggering for existing rows`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.272 | `Subject: Workflow shows Active but hasn't fired in 3 days despite new rows`... |
| 2 | 0.398 | `Subject: Can we get retroactive processing for rows added before the workflow was turned on?`... |
| 3 | 0.625 | `# Getting Started with Cobalt Loop` — Cobalt Loop connects your apps together... |

### 6. `how do I set up single sign-on`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.568 | `# SSO Configuration (Enterprise)` — Single sign-on is available on the Enterprise plan... |
| 2 | 0.749 | `Subject: Locked out of account after enabling SSO enforcement`... |
| 3 | 0.777 | `# API Reference: Triggers & Actions` — Listing available trigger/action apps... |

### 7. `what happens when I downgrade my plan`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.431 | `Subject: Question about downgrade timing` — If we downgrade from Business to Pro today... |
| 2 | 0.520 | `# Billing & Plans` — Plan comparison... |
| 3 | 0.717 | `# Data Retention Policy` — Workflow run history... |

### 8. `how do I stop duplicate messages being sent`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.431 | `Subject: Duplicate Slack messages for the same signup event` — Every new signup sends two... |
| 2 | 0.755 | `Subject: Slack action failing with channel_not_found` — Our SendMessage action... |
| 3 | 0.765 | `# Slack Integration` — Connecting Slack... |

---

## Exact-Term Queries

These queries intentionally test cases where vector search alone is expected to be weaker. They are useful baseline cases for a future hybrid/vector + keyword retrieval upgrade.

### 9. `AUTH_KEY_REVOKED`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.351 | `Subject: API key stopped working right after rotation` — Rotated our key 30 seconds ago... |
| 2 | 0.570 | `# Authentication & API Keys` — All requests to the Cobalt Loop REST API must include a valid API key... |
| 3 | 0.643 | `Subject: SAML assertion signature invalid during test login`... |

### 10. `wf_9f2a1c`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.827 | `Subject: Field mapping shows blank output but no error anywhere` — Our Slack message action... |
| 2 | 0.845 | `Subject: Slack action failing with channel_not_found` — Our SendMessage action... |
| 3 | 0.846 | `# API Reference: Workflows` — Base URL: `https://api.cobaltloop.com/v1`... |

### 11. `clk_live_`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.647 | `# Authentication & API Keys` — All requests to the Cobalt Loop REST API must include a valid API key... |
| 2 | 0.736 | `Subject: Slack action failing with channel_not_found` — Our SendMessage action... |
| 3 | 0.764 | `# Slack Integration` — Connecting Slack... |

### 12. `channel_not_found`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.487 | `Subject: Slack action failing with channel_not_found` — Our SendMessage action... |
| 2 | 0.719 | `Subject: Field mapping shows blank output but no error anywhere` — Our Slack message action... |
| 3 | 0.781 | `Subject: Duplicate Slack messages for the same signup event` — Every new signup sends two... |

### 13. `Cobalt-Signature`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.566 | `Subject: Webhook signature verification always fails` — I'm computing HMAC-SHA256... |
| 2 | 0.583 | `# Authentication & API Keys` — All requests to the Cobalt Loop REST API must include a valid API key... |
| 3 | 0.592 | `# Webhooks` — Webhooks let Cobalt Loop notify your own server when a workflow event happens... |

### 14. `429`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.742 | `Subject: Getting 429 errors on our Pro plan integration` — We're seeing 429 Too Many Requests... |
| 2 | 0.927 | `# Rate Limits` — Cobalt Loop enforces rate limits per API key... |
| 3 | 0.931 | `Subject: GitHub PR merged trigger fired for a PR that was only closed`... |

### 15. `SCIM`

| Rank | Distance | Retrieved chunk |
|---:|---:|---|
| 1 | 0.552 | `Subject: Need SCIM and manual member management to coexist temporarily`... |
| 2 | 0.852 | `# Slack Integration` — Connecting Slack... |
| 3 | 0.901 | `# GitHub Integration` — Connecting GitHub... |

---

# Week 4 Day 4 Baseline

**Retrieval configuration:**

```text
Retriever: Chroma vector search
Embedding model: sentence-transformers/all-MiniLM-L6-v2
Embedding dimensions: 384
Distance metric: cosine
top_k: 3
Query count: 15
```

This file represents the **baseline snapshot** for the current vector-only retrieval implementation.

Do not replace these recorded results when improving retrieval. Instead, add a new comparison section or a separate evaluation result so that Week 4 Day 4 remains reproducible.

---

# Week 5 Evaluation Seed

The 15 queries above should be reused as the initial seed for the Week 5 evaluation harness.

Suggested evaluation structure:

```text
Query
  ↓
Retriever
  ↓
Top-k results
  ↓
Expected relevant chunk(s)
  ↓
Hit@k / Recall@k
  ↓
Compare:
  Vector-only
  vs
  Hybrid / keyword + vector
```

The exact query strings should remain unchanged when comparing retrieval versions.

---

# Original Query Set

```python
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
```
