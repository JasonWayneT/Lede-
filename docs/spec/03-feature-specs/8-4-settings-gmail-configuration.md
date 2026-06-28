# Story 8.4: Settings -- Gmail Configuration

Status: ready-for-dev

## Story

As a user,
I want to change my Gmail label and re-authorize OAuth from Settings,
so that I can reconfigure my Gmail source at any time without re-running the full onboarding wizard.

## Acceptance Criteria

1. **Given** the Settings -- Gmail section, **When** I view it, **Then** the current configured label is shown in an editable text field

2. **Given** I change the label and click Save, **When** the save completes, **Then** the new label is stored in config and takes effect on the next Run

3. **Given** I click "Re-authorize Gmail", **When** the button is clicked, **Then** the Google OAuth browser flow opens; on completion the new token replaces the old one in the credential store

4. **Given** the current OAuth token status, **When** shown in Settings, **Then** it displays "Authorized" or "Not authorized" with the authorized email address if known

## Tasks / Subtasks

- [ ] Implement `GET /api/settings/gmail` in `app/api/settings.py` (AC: 1, 4)
  - [ ] Return: `{"data": {"label": config.gmail_label, "oauth_status": "authorized"|"not_authorized", "authorized_email": "user@gmail.com"|null}}`
  - [ ] Check `credentials.get(credentials.GMAIL_OAUTH_TOKEN)` — if None: `oauth_status = "not_authorized"`
  - [ ] If token present: parse JSON to extract `email` field (stored in token by google-auth)

- [ ] Implement `PUT /api/settings/gmail` in `app/api/settings.py` (AC: 2)
  - [ ] Accept `{"label": "Newsletters"}` body
  - [ ] Persist `gmail_label` to a settings file: `data/settings.json` (or update env-based config — see dev notes)
  - [ ] Return `{"data": {"label": new_label}}`

- [ ] Implement `POST /api/settings/gmail/reauthorize` (AC: 3)
  - [ ] Trigger `gmail.authorize()` — opens browser OAuth flow
  - [ ] On completion: new token stored via `credentials.set()`
  - [ ] Return `{"data": {"oauth_status": "authorized", "authorized_email": "..."}}`

- [ ] Add Settings -- Gmail section to `app/templates/settings.html` (AC: 1–4)
  - [ ] Label text field with save button (HTMX PUT)
  - [ ] OAuth status indicator (Authorized / Not authorized)
  - [ ] "Re-authorize Gmail" button

- [ ] Write tests in `tests/api/test_settings.py` (AC: 1, 2, 4)
  - [ ] Test GET returns current label and oauth_status
  - [ ] Test PUT updates label

## Dev Notes

### Settings persistence

`AppConfig` reads from env vars at startup. Changing settings at runtime requires persisting to a file that is re-read on next startup (or immediately loaded). Recommended approach: `data/settings.json` stores user-configured settings that override env var defaults. `AppConfig` loads this file on instantiation (lowest priority after env vars).

This pattern means `PUT /api/settings/*` writes to `data/settings.json` and `AppConfig` is re-instantiated after each write (or the in-memory config is mutated — simpler for V1).

For V1: directly mutate `AppConfig` in-memory + write to `data/settings.json` for persistence across restarts.

### Re-authorize in a browser (not via HTTP)

`gmail.authorize()` opens a browser window via `InstalledAppFlow.run_local_server()`. This blocks until the user completes OAuth. This should be called in a BackgroundTask or thread to avoid blocking the FastAPI event loop.

### Email from token

Token JSON from google-auth contains an `id_token` or the gmail API can return the authorized user's email. Simplest: after OAuth, call `gmail_service.users().getProfile(userId="me").execute()["emailAddress"]` and store alongside the token.

### References

- [Source: docs/ARCHITECTURE.md § "Authentication & Security — keyring namespace"] — `gmail_oauth_token`
- [Source: docs/epics-stories.md § "Story 8.4"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
