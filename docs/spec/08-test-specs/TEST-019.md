# Test Spec: TEST-019 Transient compression and seamless loop

## Metadata

- Test ID: `TEST-019`
- Type: unit
- Status: passing
- Related requirements: `BUG-007`
- Related acceptance criteria: `AC-087`, `AC-088`, `AC-089`

## Purpose

Proves `_compress_transients` reduces a brief high-amplitude transient's peak while leaving a
distant quiet region materially unchanged; `_loop_to_length`'s crossfaded loop unit has no
seam discontinuity larger than ordinary sample-to-sample variation; and `_moving_average` no longer
exhibits the zero-padding edge artifact that falsely dipped gain near clip boundaries.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/services/test_mixing.py`

## Expected result

- All tests pass (exit code 0)

## Automation notes

- Test file: `briefing/tests/services/test_mixing.py`
- Command: `uv run pytest -q tests/services/test_mixing.py`
