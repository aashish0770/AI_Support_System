# API Reference: Triggers & Actions

## Listing available trigger/action apps

```
GET /apps
```

Returns every app available to connect, with the trigger and action events each one supports.

```json
{
  "data": [
    {
      "app": "slack",
      "triggers": ["new_message", "new_reaction"],
      "actions": ["send_message", "create_channel", "invite_user"]
    }
  ]
}
```

## Connecting an app account

Before a workflow can use an app, the app must be connected to your Cobalt Loop account under an OAuth or API-key connection.

```
POST /connections
```

Body:
```json
{ "app": "slack" }
```

Returns an `authorization_url` your user must visit to complete OAuth. For apps that use API-key auth instead of OAuth (for example, Cobalt Loop's own webhook action, which needs no external connection), this endpoint isn't required.

## Manually firing a trigger for testing

```
POST /workflows/{workflow_id}/test-trigger
```

Body: a sample payload matching the shape of the real trigger event. Use this to validate field mapping before activating a workflow — equivalent to clicking **Test Run** in the dashboard (see [Getting Started](getting-started.md)).

## Field mapping syntax

When mapping a trigger's output field into an action's input, reference it using `{{trigger.field_name}}`. For multi-step workflows, reference an earlier action step's output using `{{steps.<step_id>.field_name}}`.

Example: mapping a Google Sheets row's `email` column into a Slack message:
```json
{ "message": "New signup: {{trigger.email}}" }
```

Unresolved field references (a typo in `field_name`, or referencing a step that hasn't run yet) resolve to an empty string at runtime rather than causing the workflow to fail — check **Run History** if a workflow's output looks unexpectedly blank.