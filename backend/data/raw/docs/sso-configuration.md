# SSO Configuration (Enterprise)

Single sign-on is available on the Enterprise plan and supports SAML 2.0 and OIDC.

## Setting up SAML SSO

1. Go to **Settings → Security → SSO** (only visible on Enterprise accounts).
2. Choose **SAML 2.0**.
3. Cobalt Loop generates a unique **Assertion Consumer Service (ACS) URL** and **Entity ID** for your account — copy both into your identity provider's app configuration (Okta, Azure AD, OneLogin, etc.).
4. Upload your identity provider's metadata XML, or manually enter the SSO URL and X.509 certificate.
5. Send a test login to confirm the connection before enforcing SSO account-wide.

## Enforcing SSO

Once verified working, toggle **Require SSO for all members**. After enabling this:

- Existing members who authenticated with email/password are logged out and must re-authenticate via SSO on next login.
- New members can only be added via your identity provider's group/app assignment — direct invites by email are disabled while SSO enforcement is active.
- Account owners retain an emergency email/password fallback login, documented separately and only shared with the account's designated technical contact, specifically to prevent a misconfigured IdP from causing a full account lockout.

## SCIM provisioning

Enterprise accounts can additionally enable SCIM to automatically provision and deprovision team members based on your identity provider's group membership, rather than manually managing Cobalt Loop team membership. SCIM and manually-managed membership should not be used simultaneously — enabling SCIM converts all manually-added members to SCIM-managed on the next sync, which may unexpectedly remove members not present in the configured IdP group.

## Common issues

- **"Assertion signature invalid" during test login** — the uploaded X.509 certificate doesn't match the one your IdP is actually signing assertions with; re-download the current metadata from your IdP rather than reusing a previously saved copy, since IdP certificates rotate periodically.
- **Users locked out immediately after enforcing SSO** — confirm every active team member is actually assigned to the Cobalt Loop app in your identity provider *before* enforcing; a member not assigned in the IdP has no way to complete SSO login and will be unable to sign in until enforcement is disabled or they're assigned.