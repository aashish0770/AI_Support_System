# API Reference: Workflows

Base URL: `https://api.cobaltloop.com/v1`

## List workflows

```
GET /workflows
```

Query parameters:
- `status` (optional) — filter by `draft`, `active`, or `paused`
- `limit` (optional, default 20, max 100)
- `cursor` (optional) — pagination cursor from a previous response

Response:
```json
{
  "data": [
    {
      "id": "wf_9f2a1c",
      "name": "New signup to Slack",
      "status": "active",
      "created_at": "2026-03-11T09:22:00Z"
    }
  ],
  "next_cursor": "eyJvZmZzZXQiOjIwfQ=="
}
```

## Get a single workflow

```
GET /workflows/{workflow_id}
```

Returns `404 WORKFLOW_NOT_FOUND` if the ID doesn't exist or doesn't belong to your account.

## Create a workflow

```
POST /workflows
```

Body:
```json
{
  "name": "New signup to Slack",
  "trigger": { "app": "google_sheets", "event": "new_row" },
  "actions": [
    { "app": "slack", "event": "send_message" }
  ]
}
```

Workflows are created in `draft` status by default. Use the activate endpoint below to turn them on.

## Activate / pause a workflow

```
PATCH /workflows/{workflow_id}/status
```

Body: `{ "status": "active" }` or `{ "status": "paused" }`

Note: setting status to `paused` does not queue trigger events that arrive while paused — see [Getting Started](getting-started.md#workflow-states) for details on this behavior.

## Delete a workflow

```
DELETE /workflows/{workflow_id}
```

Deleting a workflow also deletes its run history after 30 days. Export run history first via `GET /workflows/{workflow_id}/runs` if you need to keep it.