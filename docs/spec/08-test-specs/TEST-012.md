# Test Spec: TEST-012 Settings API form-encoded PUT contract

## Metadata

- Test ID: `TEST-012`
- Type: integration
- Status: passing
- Related requirements: `FR-022`, `FR-026`, `FR-012`, `BUG-002`
- Related acceptance criteria: `AC-061`, `AC-062`, `AC-063`, `AC-064`

## Purpose

Proves that `PUT /api/settings/gmail`, `PUT /api/settings/schedule`, and `PUT /api/settings/tts`
correctly read and validate form-encoded (`application/x-www-form-urlencoded`) request bodies —
the shape the real `settings.html` htmx forms actually send — rather than JSON.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/api/test_settings.py`

## Expected result

- All tests pass (exit code 0)
- `test_put_gmail_label` posts form data and gets back the posted label, not the route default
- `test_put_schedule_invalid_cadence`, `test_put_tts_orpheus_no_cuda_returns_400`,
  `test_put_tts_invalid_engine_returns_400` post invalid form values and get `400`

## Regression coverage

- Related bug IDs: `BUG-002`
- Known failure modes prevented: sending `json=` to a `Form(...)`-parameter route silently falls
  back to defaults instead of erroring, masking both incorrect values being persisted and missing
  validation.

## Automation notes

- Test file: `briefing/tests/api/test_settings.py`
- Command: `uv run pytest -q tests/api/test_settings.py`
- Fixtures: `async_client` (`tests/api/conftest.py`)
- Mocking: `patch.object(s, "_save_settings")` to avoid filesystem writes; `patch("app.services.tts.cuda_available", ...)` for CUDA gating
