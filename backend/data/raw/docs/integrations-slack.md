# Slack Integration

## Connecting Slack

1. Go to **Settings → Connected Apps → Slack → Connect**.
2. You'll be redirected to Slack to authorize Cobalt Loop. Choose the workspace you want to connect.
3. Approve the requested scopes: `chat:write`, `channels:read`, `users:read`.

Cobalt Loop connects at the workspace level, not the channel level — once connected, any workflow on your account can post to any channel the connected bot user has been invited to.

## Available triggers

- **New message** — fires when a message is posted in a channel you specify. Does not fire for messages posted by the Cobalt Loop bot itself, to avoid workflow loops.
- **New reaction** — fires when an emoji reaction is added to any message in a specified channel.

## Available actions

- **Send message** — post a message to a channel or DM a user. Supports Slack's Block Kit formatting via a raw JSON field for advanced layouts.
- **Create channel** — creates a new public or private channel.
- **Invite user** — invites a user (by email or Slack user ID) to a channel.

## Common issues

- **"channel_not_found" error on Send Message action** — the connected bot user hasn't been invited to that channel yet. Invite `@Cobalt Loop` to the channel manually in Slack, then retry.
- **Messages post successfully but formatting looks wrong** — the Block Kit JSON field expects Slack's block format, not plain Markdown; plain text sent to that field is escaped and posted literally rather than rendered.
- **Trigger stopped firing after working previously** — check **Settings → Connected Apps → Slack** for a "Reconnect required" banner; Slack OAuth tokens can be invalidated if a workspace admin revokes app access, independent of anything in Cobalt Loop.