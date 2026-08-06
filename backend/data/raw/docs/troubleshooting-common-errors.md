# Troubleshooting Common Errors

## Workflow runs but the action doesn't happen

Most commonly caused by:
- The connected app account's OAuth token expired — reconnect the app under **Settings → Connected Apps**.
- A required field on the action step wasn't mapped and resolved to empty (see [API Reference: Triggers & Actions](api-reference-triggers-actions.md#field-mapping-syntax)) — check the run's detail view for the exact payload sent.
- The action app itself rejected the request — check **Run History → [specific run] → Action Response** for the raw error returned by the third-party app.

## "Trigger not firing" when new data clearly exists

- If the trigger is polling-based (checks periodically rather than receiving a webhook), there can be a delay of up to 15 minutes depending on your plan's polling frequency.
- Confirm the workflow is in `active` status, not `paused` or `draft`.
- Some triggers only fire for data created *after* the workflow was activated — historical/pre-existing data is not retroactively processed.

## `429` errors from the Cobalt Loop API

You've exceeded your per-minute rate limit. See [Rate Limits](rate-limits.md) for exact limits per plan and the `Retry-After` header behavior.

## `401 AUTH_KEY_REVOKED` on requests using a key you believe is active

API keys take effect and revoke within 60 seconds, but not instantly. If you just rotated a key, wait a minute and retry. If the error persists beyond that, confirm you're using the new key and not a cached/hardcoded old one somewhere in your integration.

## Webhook deliveries failing repeatedly

See [Webhooks](webhooks-setup.md#retry-behavior) for retry timing, and [Webhooks — Common Issues](webhooks-setup.md#common-issues) for firewall and signature-verification troubleshooting.

## Data appears duplicated in the destination app

Usually caused by a workflow being activated twice (e.g. by two team members independently, unaware of each other), resulting in the same trigger event being processed by two separate workflow instances. Check **Settings → Workflow → Duplicate Detection** to see if two active workflows share the same trigger configuration.