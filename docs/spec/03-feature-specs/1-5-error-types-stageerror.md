# Story 1.5: Error Types -- StageError and Error Code Constants

Status: ready-for-dev

## Story

As a developer,
I want a StageError exception class and error code constants defined in app/core/errors.py,
so that all pipeline stages raise consistent structured errors that orchestrators and API handlers can interpret.

## Acceptance Criteria

1. **Given** a pipeline stage encountering a failure, **When** it raises `StageError("embed", "FAISS index failed", retryable=True)`, **Then** the exception carries `stage_name="embed"`, `message="FAISS index failed"`, `retryable=True`

2. **Given** a `StageError` instance, **When** I access its attributes, **Then** `stage_name` (str), `message` (str), and `retryable` (bool) are all accessible

3. **Given** `app/core/errors.py`, **When** I inspect it, **Then** error code constants are defined: `STAGE_FAILED`, `AUTH_ERROR`, `PROVIDER_UNAVAILABLE`, `VALIDATION_ERROR`, `NOT_FOUND`

4. **Given** a stage catching a raw exception, **When** it re-raises, **Then** it always wraps in `StageError` — no raw `Exception` or `RuntimeError` propagates from stage code

5. **Given** the errors module, **When** imported by stages, orchestrator, and API handlers, **Then** no circular imports occur — `errors.py` imports only from Python stdlib

## Tasks / Subtasks

- [ ] Implement `app/core/errors.py` (AC: 1–5)
  - [ ] Define error code constants as module-level strings: `STAGE_FAILED = "STAGE_FAILED"`, `AUTH_ERROR = "AUTH_ERROR"`, `PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"`, `VALIDATION_ERROR = "VALIDATION_ERROR"`, `NOT_FOUND = "NOT_FOUND"`
  - [ ] Implement `StageError(Exception)` with `__init__(self, stage_name: str, message: str, retryable: bool = True, code: str = STAGE_FAILED)`
  - [ ] Assign all params as instance attributes in `__init__`
  - [ ] Implement `__str__` returning `f"[{self.stage_name}] {self.message}"`
  - [ ] No imports beyond Python stdlib

- [ ] Register `StageError` handler in `app/main.py` (AC: 1)
  - [ ] `@app.exception_handler(StageError)` returning JSON: `{"error": str(exc), "code": exc.code, "stage": exc.stage_name, "retryable": exc.retryable}` with HTTP 500

- [ ] Write tests in `tests/test_errors.py` or `tests/api/test_errors.py` (AC: 1–3, 5)
  - [ ] Test `StageError` attribute access
  - [ ] Test all constants have expected string values
  - [ ] Test `StageError` default `retryable=True`
  - [ ] Test `__str__` format

## Dev Notes

### Why no code duplication

The error code constants (`STAGE_FAILED`, etc.) are used in three places: SSE event payloads, REST error envelopes, and `StageError.code`. Centralizing in `errors.py` ensures all three consumers use the same strings.

### Retryable semantics

- `retryable=True` → orchestrator runs 3-tier retry sequence
- `retryable=False` → orchestrator skips retry, immediately enters Hold state
- Auth errors (`AUTH_ERROR`) are always `retryable=False`
- Provider unavailable errors (`PROVIDER_UNAVAILABLE`) are `retryable=True`

### Stage wrapping pattern (all stages must follow)

```python
from app.core.errors import StageError, STAGE_FAILED

async def run(packet, config):
    try:
        ...
    except Exception as e:
        raise StageError("stage_name", str(e), retryable=True) from e
```

The `from e` preserves the original traceback for logging.

### References

- [Source: docs/ARCHITECTURE.md § "API & Communication — Error Envelope"] — `{"error": "...", "code": "STAGE_FAILED", "stage": "...", "retryable": true}`
- [Source: docs/ARCHITECTURE.md § "Process Patterns — Error Handling"] — wrapping and propagation rules
- [Source: docs/epics-stories.md § "Story 1.5"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implemented error code constants and `StageError` with structured attributes and `__str__` formatting.
- Registered a FastAPI exception handler returning the standardized error envelope.
- Added tests covering constants, `StageError` behavior, and handler envelope via ASGI transport.
- Verification: `uv run pytest -q tests/test_errors.py` (PASS).

### File List

- `briefing/app/core/errors.py`
- `briefing/app/main.py`
- `briefing/tests/test_errors.py`
