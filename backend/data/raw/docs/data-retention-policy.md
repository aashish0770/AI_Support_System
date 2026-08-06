# Data Retention Policy

## Workflow run history

Run history (including the data that passed through each trigger and action step) is retained for:

- **Free / Pro plans:** 30 days
- **Business plan:** 90 days
- **Enterprise plan:** configurable, up to 2 years

After the retention period, run history is permanently deleted and cannot be recovered. Deleting a workflow also deletes its run history after the standard 30-day grace period regardless of plan (see [API Reference: Workflows](api-reference-workflows.md#delete-a-workflow)).

## Data in transit vs. data at rest

Data passing through a workflow (trigger payloads, action inputs/outputs) is encrypted in transit (TLS 1.2+) between Cobalt Loop and connected apps. Run history data at rest is encrypted using AES-256.

Cobalt Loop does not store the full response body of every action indefinitely by default — only a truncated preview (first 10KB) is retained in run history for storage efficiency, unless **Settings → Workflow → Full Payload Logging** is explicitly enabled, which is disabled by default due to the potential for sensitive data (e.g. customer PII passing through a workflow) to be retained longer than intended.

## Account deletion

Deleting your Cobalt Loop account removes all workflows, connections, and run history within 30 days. Connected third-party apps (Slack, GitHub, etc.) are **not** automatically disconnected on their end — revoke Cobalt Loop's access directly in each connected app's settings if required for compliance purposes.

## Data export

Before deleting an account or downgrading in a way that reduces retention, export data via:
```
GET /workflows/{workflow_id}/runs?format=export
```
Exports are available as a downloadable JSON or CSV file and do not count against API rate limits.