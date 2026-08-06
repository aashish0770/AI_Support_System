# Webhooks

Webhooks let Cobalt Loop notify your own server when a workflow event happens, instead of (or in addition to) using a built-in action.

## Setting up a webhook action

1. In a workflow, add a new action step and choose **Webhook** as the action app.
2. Enter the destination URL. It must be `https://` — plain `http://` URLs are rejected at save time.
3. Choose the HTTP method (`POST`, `PUT`, or `PATCH`).
4. Map fields from earlier steps into the JSON body.

## Verifying webhook signatures

Every webhook request includes a `Cobalt-Signature` header, computed as an HMAC-SHA256 of the raw request body using your workflow's signing secret (found in the webhook action's settings).

To verify a request is genuinely from Cobalt Loop:

1. Compute `HMAC-SHA256(signing_secret, raw_body)`.
2. Compare it to the `Cobalt-Signature` header using a constant-time comparison.
3. Reject the request if they don't match.

Requests older than 5 minutes (based on the `Cobalt-Timestamp` header) should also be rejected, to prevent replay attacks.

## Retry behavior

If your endpoint doesn't respond with a `2xx` status within 10 seconds, Cobalt Loop retries the webhook with exponential backoff:

- Retry 1: after 30 seconds
- Retry 2: after 2 minutes
- Retry 3: after 10 minutes
- Retry 4 (final): after 1 hour

After 4 failed attempts, the webhook delivery is marked **Failed** and will not be retried further. Failed deliveries are visible under **Workflow → Run History** and can be manually replayed for up to 7 days.

## Common issues

- **Webhook shows as delivered but nothing happened on my server** — check that your endpoint isn't behind a firewall or VPN that blocks Cobalt Loop's IP ranges (listed in **Settings → Webhook IP Allowlist**).
- **Signature verification always fails** — make sure you're hashing the *raw* request body, not a re-serialized/re-parsed version of it, since re-serializing JSON can change key ordering or whitespace and produce a different hash.