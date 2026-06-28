# Story 1.4: Credential Store -- Keyring Wrapper

Status: ready-for-dev

## Story

As a developer,
I want a centralized credential module that reads and writes secrets to the OS keychain under the "briefing" service namespace,
so that no other module needs to know about keyring directly and credentials are never stored in plaintext.

## Acceptance Criteria

1. **Given** the credentials module, **When** I call `credentials.set("gmail_oauth_token", token_json)`, **Then** the token is stored in the OS keychain under `service="briefing"`, `username="gmail_oauth_token"`

2. **Given** a stored credential, **When** I call `credentials.get("gmail_oauth_token")`, **Then** the stored value is returned as a string

3. **Given** a key that has not been set, **When** I call `credentials.get("openai_key")`, **Then** `None` is returned (not an exception)

4. **Given** the credentials module, **When** I call `credentials.delete("anthropic_key")`, **Then** the keychain entry is removed; subsequent `get()` returns `None`

5. **Given** all valid credential key names, **When** I inspect the module, **Then** constants `gmail_oauth_token`, `openai_key`, `anthropic_key`, `gemini_key` are defined at module level — no other module hardcodes these strings

6. **Given** any credential operation, **When** it runs on Windows, macOS, or Linux, **Then** the native OS keychain is used without additional configuration

## Tasks / Subtasks

- [ ] Implement `app/core/credentials.py` (AC: 1–6)
  - [ ] Import `keyring` (already installed via Story 1.1)
  - [ ] Define module-level string constants: `GMAIL_OAUTH_TOKEN = "gmail_oauth_token"`, `OPENAI_KEY = "openai_key"`, `ANTHROPIC_KEY = "anthropic_key"`, `GEMINI_KEY = "gemini_key"`
  - [ ] `SERVICE_NAME = "briefing"` — always this exact string, never varies
  - [ ] Implement `def set(key: str, value: str) -> None`: calls `keyring.set_password(SERVICE_NAME, key, value)`
  - [ ] Implement `def get(key: str) -> str | None`: calls `keyring.get_password(SERVICE_NAME, key)` — returns `None` if not found
  - [ ] Implement `def delete(key: str) -> None`: calls `keyring.delete_password(SERVICE_NAME, key)` — catches `keyring.errors.PasswordDeleteError` if not found (does not raise)
  - [ ] No other module calls `keyring` directly — enforce via code review

- [ ] Write tests in `tests/services/test_credentials.py` (AC: 1–5)
  - [ ] Mock `keyring.set_password`, `keyring.get_password`, `keyring.delete_password` using `unittest.mock.patch`
  - [ ] Test `get()` returns `None` when keyring returns `None` (key not found)
  - [ ] Test `delete()` does not raise when key does not exist
  - [ ] Test constants are defined at module level with exact string values

## Dev Notes

### keyring library behavior

`keyring` automatically selects the OS backend:
- Windows: Windows Credential Manager
- macOS: Keychain
- Linux: libsecret / GNOME Keyring (may require `SecretService` daemon)

In CI or headless environments, `keyring` may fall back to an in-memory store or raise `NoKeyringError`. Tests should mock keyring entirely to avoid CI failures.

### No custom encryption

`keyring` uses OS-native encryption. Do NOT add a custom encryption layer on top. The architecture decision is to rely on OS keychain — no custom key management.

### Constants naming

Use `UPPER_SNAKE_CASE` constants per architecture naming conventions. Expose them as module-level: `credentials.GMAIL_OAUTH_TOKEN`, etc. Stages and services that need to read credentials import the constant, not the string literal.

### Entry point isolation

`credentials.py` imports only `keyring` and stdlib. It must not import from `api/`, `pipeline/`, `db/`, or entry points.

### References

- [Source: docs/ARCHITECTURE.md § "Authentication & Security — keyring namespace"] — service name and key names
- [Source: docs/ARCHITECTURE.md § "Enforcement Guidelines"] — "Use the exact keyring service name and exact key names defined in credentials.py"
- [Source: docs/epics-stories.md § "Story 1.4"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implemented centralized keyring wrapper with fixed `SERVICE_NAME = "briefing"` and module-level key constants.
- Implemented `set/get/delete` with safe delete semantics (missing key does not raise).
- Added unit tests that fully mock `keyring` (no OS keychain access).
- Verification: `uv run pytest -q tests/services/test_credentials.py` (PASS).

### File List

- `briefing/app/core/credentials.py`
- `briefing/tests/services/test_credentials.py`
