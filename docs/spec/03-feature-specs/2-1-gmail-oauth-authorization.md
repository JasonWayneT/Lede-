# Story 2.1: Gmail OAuth Authorization

Status: ready-for-dev

## Story

As a user setting up Briefing for the first time,
I want to authorize Gmail access through a browser OAuth flow,
so that the app can read my newsletter emails without me managing credentials manually.

## Acceptance Criteria

1. **Given** a user running `setup.py` for the first time, **When** they reach the Gmail authorization step, **Then** their default browser opens to the Google OAuth consent screen with read-only Gmail scope

2. **Given** a successful OAuth authorization, **When** the browser redirects back to the local callback, **Then** the resulting token JSON is stored via `credentials.set("gmail_oauth_token", ...)` — not on the filesystem in plaintext

3. **Given** a stored OAuth token, **When** the Gmail service makes an API call, **Then** `google-auth` automatically refreshes the token if expired, without prompting the user again

4. **Given** a revoked or invalid token, **When** the Gmail service attempts an API call, **Then** a `StageError` with `code=AUTH_ERROR` and `retryable=False` is raised with a clear message instructing the user to re-authorize from Settings

5. **Given** the OAuth scope requested, **When** I inspect the credentials.json and token, **Then** only the Gmail read-only scope is requested — no write, send, or modify permissions

## Tasks / Subtasks

- [ ] Implement OAuth flow in `app/services/gmail.py` (AC: 1, 2, 5)
  - [ ] Use `google_auth_oauthlib.flow.InstalledAppFlow` with scope `["https://www.googleapis.com/auth/gmail.readonly"]`
  - [ ] `flow.run_local_server(port=0)` opens browser and handles callback automatically
  - [ ] After successful flow, serialize `credentials.to_json()` and call `app.core.credentials.set(credentials.GMAIL_OAUTH_TOKEN, token_json)`
  - [ ] `setup.py` calls `gmail.authorize()` during onboarding

- [ ] Implement `gmail.get_service()` with auto-refresh (AC: 3, 4)
  - [ ] Load token JSON from `credentials.get(credentials.GMAIL_OAUTH_TOKEN)`
  - [ ] Deserialize with `google.oauth2.credentials.Credentials.from_authorized_user_info(json.loads(token_json))`
  - [ ] Build service: `googleapiclient.discovery.build("gmail", "v1", credentials=creds)`
  - [ ] `google-auth` handles token refresh automatically on each API call via the credentials object
  - [ ] Wrap `google.auth.exceptions.TransportError` and `google.auth.exceptions.RefreshError` in `StageError(stage_name, ..., code=AUTH_ERROR, retryable=False)` with message: "Gmail token invalid or revoked. Re-authorize from Settings."

- [ ] Write tests in `tests/services/test_gmail.py` (AC: 3, 4)
  - [ ] Mock `google.oauth2.credentials.Credentials` to simulate expired token that refreshes
  - [ ] Mock `RefreshError` to test `StageError(code=AUTH_ERROR, retryable=False)` is raised
  - [ ] Verify token is stored via `credentials.set`, not written to file

## Dev Notes

### Google Cloud prerequisite

User must have `credentials.json` (OAuth client secrets file) in the project root before `setup.py` runs. `setup.py` looks for it there. This file is gitignored. The README (Story 12.5) explains how to create it.

### Scope — read-only only

`https://www.googleapis.com/auth/gmail.readonly` — this is the minimum required scope. Do NOT request `gmail.modify`, `gmail.send`, or any broader scope.

### Token storage

Token is a JSON string containing `access_token`, `refresh_token`, `token_uri`, `client_id`, `client_secret`, `scopes`. Store the entire JSON string via `credentials.set()`. Never write to a `token.json` file on disk.

### Auto-refresh

`google.oauth2.credentials.Credentials` auto-refreshes when `credentials.expired` is True and a `refresh_token` is present. The `googleapiclient` service call triggers this automatically.

### gmail_label config

`AppConfig.gmail_label` controls which label is filtered. `get_service()` does not need the label — that's the fetch service's concern (Story 2.2).

### References

- [Source: docs/ARCHITECTURE.md § "External Integrations — Gmail API"] — `services/gmail.py`, OAuth token via `core/credentials.py`
- [Source: docs/ARCHITECTURE.md § "Authentication & Security"] — keyring namespace, no CSRF (localhost only)
- [Source: docs/epics-stories.md § "Story 2.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implemented Gmail OAuth flow using `InstalledAppFlow` with `gmail.readonly` scope and local callback server.
- Token is stored via `app.core.credentials.set(GMAIL_OAUTH_TOKEN, token_json)`; no token file is written.
- Implemented `gmail.get_service()` with refresh and `AUTH_ERROR` wrapping for invalid/revoked tokens.
- Verification: `uv run pytest -q tests/services/test_gmail.py` (PASS).

### File List

- `briefing/app/services/gmail.py`
- `briefing/setup.py`
- `briefing/tests/services/test_gmail.py`
