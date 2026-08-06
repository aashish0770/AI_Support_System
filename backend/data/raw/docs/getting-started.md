# Getting Started with Cobalt Loop

Cobalt Loop connects your apps together so data moves automatically between them. A **workflow** watches for a **trigger** event in one app and runs one or more **actions** in other apps when it fires.

## Creating your first workflow

1. From the dashboard, click **New Workflow**.
2. Choose a trigger app and event (for example, "New row in Google Sheets").
3. Choose one or more action apps and events (for example, "Send message in Slack").
4. Map fields from the trigger's output to each action's input fields.
5. Click **Activate** to turn the workflow on.

Workflows run automatically once activated. You can pause a workflow at any time from the workflow list without deleting it.

## Workflow states

A workflow can be in one of three states:

- **Draft** — created but not activated. No trigger events are processed.
- **Active** — running normally. Trigger events are processed as they arrive.
- **Paused** — temporarily stopped. Trigger events that arrive while paused are **not** queued or replayed once you reactivate; they are simply missed.

## Testing a workflow before activating

Use the **Test Run** button on any draft workflow to send a single sample trigger event through the workflow without affecting live data. Test runs never count against your monthly task usage.

## Next steps

- See [Authentication & API Keys](authentication-api-keys.md) if you're building against the Cobalt Loop API directly rather than using the dashboard.
- See [Rate Limits](rate-limits.md) to understand usage caps for your plan.