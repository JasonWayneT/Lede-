# Test Spec: TEST-013 Gmail OAuth redirect flow

## Metadata

- Test ID: `TEST-013`
- Type: unit
- Status: passing
- Related requirements: `FR-001`, `BUG-003`
- Related acceptance criteria: `AC-065`

## Purpose

Proves the OAuth redirect flow (`build_auth_url()` / `exchange_code()`) — the mechanism actually
shipped since `6e0a3dd` — builds a consent URL and stores the exchanged token via
`credential_store.set()`, replacing coverage of the removed `authorize()`/`InstalledAppFlow`
local-server flow.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/services/test_gmail.py`

## Expected result

- All tests pass (exit code 0)
- `test_build_auth_url_returns_consent_url` proves `build_auth_url()` returns the URL produced by
  `Flow.authorization_url(...)`
- `test_exchange_code_stores_token_via_credentials_set` proves `exchange_code()` calls
  `Flow.fetch_token(code=...)` and then `credential_store.set(GMAIL_OAUTH_TOKEN, creds.to_json())`

## Regression coverage

- Related bug IDs: `BUG-003`
- Known failure modes prevented: OAuth token exchange silently failing to persist the token, or a
  future refactor reintroducing a blocking local-server flow inside the request handler.

## Automation notes

- Test file: `briefing/tests/services/test_gmail.py`
- Command: `uv run pytest -q tests/services/test_gmail.py`
- Mocking: `patch("app.services.gmail.get_credentials_path", ...)`, `patch("app.services.gmail.Flow")`, `patch("app.services.gmail.credential_store.set")`
