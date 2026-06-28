# Story 3.2: BYOK Provider Integration -- OpenAI, Anthropic, Gemini

Status: ready-for-dev

## Story

As a user who prefers cloud LLM quality,
I want to configure an API key for OpenAI, Anthropic, or Gemini and have all pipeline LLM calls use that provider,
so that I can get better synthesis quality by using a cloud model.

## Acceptance Criteria

1. **Given** `config.llm_provider = "openai"` and a valid `openai_key` in the credential store, **When** I call `llm.complete(prompt, config)`, **Then** the request is sent to the OpenAI Chat Completions API and the response text is returned

2. **Given** `config.llm_provider = "anthropic"` and a valid `anthropic_key`, **When** I call `llm.complete(prompt, config)`, **Then** the request uses the Anthropic Messages API via the `anthropic` SDK

3. **Given** `config.llm_provider = "gemini"` and a valid `gemini_key`, **When** I call `llm.complete(prompt, config)`, **Then** the request uses the Google Generative AI SDK

4. **Given** any BYOK provider call, **When** I inspect network traffic, **Then** the API key is sent only to the configured provider's domain — it is never logged or stored in plaintext

5. **Given** a BYOK provider with an invalid or expired API key, **When** I call `llm.complete(prompt, config)`, **Then** a `StageError` with `code=AUTH_ERROR` and `retryable=False` is raised

6. **Given** switching `config.llm_provider` from `"ollama"` to `"openai"` at runtime, **When** the next pipeline Run starts, **Then** all LLM calls in that Run use the new provider — no app restart required

## Tasks / Subtasks

- [ ] Add OpenAI branch to `llm.py` (AC: 1, 4, 5, 6)
  - [ ] Read API key: `credentials.get(credentials.OPENAI_KEY)`
  - [ ] Use `openai.AsyncOpenAI(api_key=key)`
  - [ ] Call: `client.chat.completions.create(model=config.openai_model_name, messages=[{"role": "user", "content": prompt}])`
  - [ ] Add `openai_model_name: str = "gpt-4o-mini"` to `AppConfig`
  - [ ] Catch `openai.AuthenticationError` → `StageError(code=AUTH_ERROR, retryable=False)`
  - [ ] Catch `openai.APIConnectionError` → `StageError(code=PROVIDER_UNAVAILABLE, retryable=True)`

- [ ] Add Anthropic branch to `llm.py` (AC: 2, 4, 5, 6)
  - [ ] Read API key: `credentials.get(credentials.ANTHROPIC_KEY)`
  - [ ] Use `anthropic.AsyncAnthropic(api_key=key)`
  - [ ] Call: `client.messages.create(model=config.anthropic_model_name, max_tokens=2048, messages=[{"role": "user", "content": prompt}])`
  - [ ] Add `anthropic_model_name: str = "claude-haiku-4-5-20251001"` to `AppConfig`
  - [ ] Catch `anthropic.AuthenticationError` → `StageError(code=AUTH_ERROR, retryable=False)`

- [ ] Add Gemini branch to `llm.py` (AC: 3, 4, 5, 6)
  - [ ] Read API key: `credentials.get(credentials.GEMINI_KEY)`
  - [ ] Use `google.generativeai.configure(api_key=key)` then `genai.GenerativeModel(config.gemini_model_name)`
  - [ ] Add `gemini_model_name: str = "gemini-1.5-flash"` to `AppConfig`
  - [ ] Catch auth errors → `StageError(code=AUTH_ERROR, retryable=False)`

- [ ] Write tests in `tests/services/test_llm.py` (AC: 1–5)
  - [ ] Mock each provider SDK call
  - [ ] Test `AUTH_ERROR` on invalid key for each provider
  - [ ] Test that API key is read from credentials, not from config or env
  - [ ] Test runtime provider switching (config change between calls)

## Dev Notes

### API key never logged

Do NOT log the API key value at any log level. When logging provider calls, log only `provider`, `model`, `prompt_length` — never the key or its first/last characters.

### Model names in config

Add model name fields to `AppConfig` for each BYOK provider (see tasks above). These let users configure their preferred model without code changes.

### Runtime switching (AC: 6)

Runtime switching works automatically because `llm.complete()` reads `config.llm_provider` on every call and the config is re-read from credentials on every call. There is no connection pool or singleton to invalidate.

### Anthropic model naming

Current Anthropic model IDs follow the pattern `claude-{model}-{date}`. Default to `claude-haiku-4-5-20251001` (cheapest capable model). Users can override via `ANTHROPIC_MODEL_NAME` env var.

### References

- [Source: docs/ARCHITECTURE.md § "Process Patterns — LLM Provider Routing"] — provider enum, `llm.py` owns all routing
- [Source: docs/ARCHITECTURE.md § "Authentication & Security — keyring namespace"] — key names
- [Source: docs/epics-stories.md § "Story 3.2"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
