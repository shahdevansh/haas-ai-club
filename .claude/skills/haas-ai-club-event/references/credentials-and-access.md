# Credentials and access

## Sources of access

| System | Auth | Notes |
|---|---|---|
| Haas EMS (rooms) | CalNet + Duo | Interactive Duo approval by the organizer; sessions expire fast |
| CampusGroups | CalNet-backed organizer login | Officer role required to create events |
| CalLink (reimbursements) | CalNet + Duo | Signatory/requestor role required |
| GitHub (website) | GitHub account with push rights | Only owner pushes auto-deploy |
| Email blast | Club/organizer email account | Draft first, always |
| DoorDash (food orders) | Organizer's DoorDash account via dd-cli | Headless: two-step `export-token`, token as `DD_CLI_ACCESS_TOKEN`; ~72h expiry, never in chat |
| Figma (design assets) | The Google account linked to the club Figma | Read official assets from the latest board |

## Rules

- Credentials come from the host harness's secret store (its vault, keychain,
  environment injection, or credential manager). **Never ask for a password in
  chat, never accept one sent in chat, never write one into a file, repo, or
  log.** If the harness has no secret store, stop and have the human perform
  the login themselves.
- Duo is live and interactive: warn the organizer a push is coming and expect
  a tap within a minute. **Retry only with the organizer's knowledge and at
  most a bounded number of times** (suggest one resend, then pause and ask) -
  never fire repeated pushes silently; duplicate pushes train people to
  approve blindly. Never attempt to enroll a new 2FA device or bypass Duo.
- If a login flow fails (Duo errors, session expiry), hand the step to the
  human rather than retry-looping. Don't promise a Duo-gated action until a
  login has actually worked in the current session.
- Each action runs as the organizer, with their plan approval covering it.
  New recipients, new spend, or new audiences need their own approval.
