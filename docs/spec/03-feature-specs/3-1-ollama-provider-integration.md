# Story 3.1: Ollama Provider Integration

Status: ready-for-dev

## Story

As a developer building pipeline stages,
I want a llm.py service that routes LLM calls to a local Ollama instance by default,
so that the pipeline works out of the box without any API keys.

## Acceptance Criteria

1. **Given** Ollama running locally with a model loaded, **When** I call `llm.complete(prompt, config)` with `config.llm_provider = "ollama"`, **Then** the request is sent to the Ollama HTTP API and the response text is returned as a plain string

2. **Given** `config.llm_provider = "ollama"` and Ollama not reachable, **When** I call `llm.complete(prompt, config)`, **Then** a `StageError` with `code=PROVIDER_UNAVAILABLE` and `retryable=True` is raised

3. **Given** `AppConfig.ollama_model_name`, **When** the provider makes the API call, **Then** the configured model name is used in the request body — not a hardcoded default

4. **Given** any LLM call in a pipeline stage, **When** I search the stage file, **Then** no direct import of `ollama` or `httpx` targeting Ollama appears — all calls go through `llm.complete()`

## Tasks / Subtasks

- [ ] Implement `app/services/llm.py` with Ollama provider (AC: 1–4)
  - [ ] Define `async def complete(prompt: str, config: AppConfig, system: str | None = None) -> str`
  - [ ] Route based on `config.llm_provider` — for Ollama: POST to `{config.ollama_base_url}/api/generate`
  - [ ] Request body: `{"model": config.ollama_model_name, "prompt": prompt, "stream": False}`
  - [ ] Parse response: return `response_json["response"]`
  - [ ] Use `httpx.AsyncClient` for the HTTP call (already installed)
  - [ ] Wrap `httpx.ConnectError`, `httpx.TimeoutException`, and non-2xx responses in `StageError("llm", message, code=PROVIDER_UNAVAILABLE, retryable=True)`
  - [ ] Use `config.ollama_model_name` — never hardcode `"llama3.2"` or any model name

- [ ] Write tests in `tests/services/test_llm.py` (AC: 1–3)
  - [ ] Mock `httpx.AsyncClient.post` to return a valid Ollama response
  - [ ] Test `PROVIDER_UNAVAILABLE` StageError on `ConnectError`
  - [ ] Test model name from config is used in request body

## Dev Notes

### Ollama API endpoint

`POST {base_url}/api/generate` with `stream: false` returns a single JSON object. The response text is in `response_json["response"]`. Do not use streaming mode for this implementation.

Alternative: use the `/api/chat` endpoint if system prompts are needed. `/api/generate` is simpler for single-turn prompts.

### Provider routing scaffold

Even though only Ollama is implemented in this story, write the `complete()` function with a provider routing structure that will be extended in Stories 3.2 and 3.3:

```python
async def complete(prompt: str, config: AppConfig, system: str | None = None) -> str:
    if config.llm_provider == "ollama":
        return await _ollama_complete(prompt, config, system)
    elif config.llm_provider in ("openai", "anthropic", "gemini", "mcp_sampling"):
        raise StageError("llm", f"Provider '{config.llm_provider}' not yet implemented", retryable=False)
    else:
        raise StageError("llm", f"Unknown provider: {config.llm_provider}", retryable=False)
```

### No direct provider imports in stages

Architecture enforcement: stages import `from app.services import llm` and call `await llm.complete(prompt, config)`. They never `import httpx` or call Ollama directly.

### References

- [Source: docs/ARCHITECTURE.md § "Process Patterns — LLM Provider Routing"] — all LLM calls through `llm.py`
- [Source: docs/ARCHITECTURE.md § "Format Patterns — API Error Envelope — code values"] — `PROVIDER_UNAVAILABLE`
- [Source: docs/epics-stories.md § "Story 3.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
