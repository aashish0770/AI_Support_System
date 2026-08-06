# Authentication & API Keys

All requests to the Cobalt Loop REST API must include a valid API key.

## Creating an API key

1. Go to **Settings → API Keys**.
2. Click **Generate New Key**.
3. Copy the key immediately — it is shown only once. If you lose it, you must revoke it and generate a new one.

## Using your API key

Include your key in the `Authorization` header of every request:

```
Authorization: Bearer clk_live_XXXXXXXXXXXXXXXXXXXX
```

Live keys are prefixed `clk_live_`. Test-mode keys (which run against sandbox data and never trigger real actions) are prefixed `clk_test_`.

## Key rotation

We recommend rotating API keys every 90 days. To rotate a key without downtime:

1. Generate a new key.
2. Update your integration to use the new key.
3. Confirm the new key is working (check **Settings → API Keys → Last Used** timestamp).
4. Revoke the old key.

Revoking a key takes effect within 60 seconds. Any requests using a revoked key after that window will receive a `401 Unauthorized` response with error code `AUTH_KEY_REVOKED`.

## Common authentication errors

| Error code | Meaning | Fix |
|---|---|---|
| `AUTH_KEY_MISSING` | No `Authorization` header sent | Add the header to your request |
| `AUTH_KEY_INVALID` | Key doesn't match any active key on the account | Check for typos, or generate a new key |
| `AUTH_KEY_REVOKED` | Key was revoked | Generate a new key |
| `AUTH_KEY_EXPIRED` | Key exceeded the 90-day recommended lifetime and was auto-expired under an Enterprise plan's key policy | Rotate the key |

See [Rate Limits](rate-limits.md) for what happens when a valid key exceeds its usage cap.