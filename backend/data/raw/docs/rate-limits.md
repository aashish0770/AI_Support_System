# Rate Limits

Cobalt Loop enforces rate limits per API key to keep the platform stable for all customers.

## Limits by plan

| Plan | Requests per minute | Monthly task executions |
|---|---|---|
| Free | 30 | 1,000 |
| Pro | 120 | 25,000 |
| Business | 300 | 100,000 |
| Enterprise | Custom | Custom |

A "task execution" counts each time a workflow runs an action step. A workflow with 3 action steps that fires once counts as 3 task executions.

## What happens when you exceed the limit

Requests beyond the per-minute limit receive a `429 Too Many Requests` response with a `Retry-After` header indicating how many seconds to wait before retrying.

Exceeding your **monthly** task execution limit does not return an error — instead, workflows continue running, but you'll be prompted to upgrade your plan, and Enterprise-tier overage billing may apply if configured on your account.

## Checking your current usage

```
GET /v1/account/usage
```

Returns your current billing period's task execution count, requests-per-minute usage, and time until your limits reset.

## Best practices to avoid hitting limits

- Use webhooks instead of polling-based triggers where possible — polling triggers count against your rate limit on every check, even when there's no new data.
- Batch related actions into a single workflow run rather than triggering multiple separate workflow runs for the same event.
- For high-volume integrations, contact sales about Enterprise custom limits before you hit the Business plan ceiling, not after.

See [Authentication & API Keys](authentication-api-keys.md) for how keys are identified for rate-limiting purposes.