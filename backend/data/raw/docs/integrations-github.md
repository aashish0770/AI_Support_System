# GitHub Integration

## Connecting GitHub

1. Go to **Settings → Connected Apps → GitHub → Connect**.
2. Authorize the Cobalt Loop GitHub App for either your entire account or specific repositories.
3. Repository access can be changed anytime from your GitHub account's **Installed Apps** settings — Cobalt Loop only sees repositories you explicitly grant access to.

## Available triggers

- **New issue** — fires when an issue is opened in a connected repository.
- **New pull request** — fires when a PR is opened.
- **PR merged** — fires when a PR is merged (not just closed — closing without merging does not fire this trigger).
- **New commit on branch** — fires on push to a specified branch.

## Available actions

- **Create issue**
- **Comment on issue/PR**
- **Add label**
- **Create pull request**

## Common issues

- **Trigger doesn't fire for a repository I know I granted access to** — confirm the repository is listed under **Settings → Connected Apps → GitHub → Repository Access**; access granted at the GitHub App level doesn't automatically sync to Cobalt Loop's workflow list until the connection is refreshed (click **Refresh Repository List**).
- **"PR merged" trigger fired for a PR I closed without merging** — this shouldn't happen; if it does, check whether the PR was merged via a squash-merge from a different tool that GitHub's API reports differently than expected, and report it to support with the PR URL.
- **Rate limit errors specifically from GitHub actions, separate from Cobalt Loop's own rate limits** — GitHub's own API rate limits apply independently per connected account; high-frequency workflows against a single GitHub App installation can hit GitHub's limits even when well within Cobalt Loop's own limits.