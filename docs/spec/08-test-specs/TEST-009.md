# Test Spec: TEST-009 Ollama request sets num_ctx

## Metadata

- Test ID: `TEST-009`
- Type: unit
- Status: passing
- Related requirements: `BUG-001`, `ARCH-006`
- Related acceptance criteria: `AC-056`

## Purpose

Proves `_ollama_complete` sends `options.num_ctx` from `config.ollama_num_ctx` on every request,
so Ollama does not silently fall back to its 2048-token default regardless of the configured
model's real context window.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/services/test_llm.py::test_ollama_complete_sets_num_ctx`

## Expected result

- Test passes (exit code 0); mocked request body contains `options.num_ctx == 8192`

## Automation notes

- Test file: `briefing/tests/services/test_llm.py`
- Command: `uv run pytest -q tests/services/test_llm.py`
