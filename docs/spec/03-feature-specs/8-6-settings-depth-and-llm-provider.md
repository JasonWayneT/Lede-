# Story 8.6: Settings -- Briefing Depth and LLM Provider

Status: ready-for-dev

## Story

As a user,
I want to select my preferred briefing depth and LLM provider -- and test the connection -- from Settings,
so that I can tune quality and cost without editing config files.

## Acceptance Criteria

1. **Given** the Settings -- Briefing Depth section, **When** I view it, **Then** Brief, Standard, and Deep options are shown with a description of each; Standard is highlighted as default

2. **Given** I select a depth and save, **When** the next Run starts, **Then** the pipeline uses the selected depth for all story framing

3. **Given** the Settings -- LLM Provider section, **When** I view it, **Then** the five provider options are listed: Ollama, OpenAI, Anthropic, Gemini, MCP Sampling

4. **Given** I select Ollama and click "Test Connection", **When** Ollama is reachable, **Then** a green "Connected" indicator appears showing the configured model name

5. **Given** I select OpenAI and enter an API key then click "Test Connection", **When** the key is valid, **Then** "Connected" indicator appears; when invalid, a clear error message appears

6. **Given** I save a BYOK API key, **When** I view Settings again, **Then** the key is masked (e.g. "sk-...abc") — the full key is never displayed after entry

## Tasks / Subtasks

- [ ] Implement depth settings endpoints in `app/api/settings.py` (AC: 1, 2)
  - [ ] `GET /api/settings/depth` → `{"data": {"briefing_depth": "standard"}}`
  - [ ] `PUT /api/settings/depth` → accepts `{"briefing_depth": "brief"|"standard"|"deep"}`, validates, persists

- [ ] Implement LLM provider settings endpoints in `app/api/settings.py` (AC: 3–6)
  - [ ] `GET /api/settings/llm` → `{"data": {"provider": "ollama", "model_name": "...", "api_key_set": true, "api_key_masked": "sk-...abc"}}`
  - [ ] `PUT /api/settings/llm` → accepts provider, model_name, api_key (optional); stores key via `credentials.set()`
  - [ ] `POST /api/settings/llm/test` → call `llm.complete("Say OK", config)` with current settings; return `{"connected": true, "model": "..."}` or `{"connected": false, "error": "..."}`

- [ ] Add Settings -- Depth and LLM UI to `app/templates/settings.html` (AC: 1–6)
  - [ ] Depth: three radio buttons with descriptions, HTMX PUT on save
  - [ ] LLM Provider: radio buttons for 5 providers; conditional API key input (shown for BYOK providers); masked display after save
  - [ ] Model name text field per provider
  - [ ] "Test Connection" button with inline result indicator

- [ ] Write tests in `tests/api/test_settings.py` (AC: 2, 5, 6)
  - [ ] Test PUT depth validates accepted values
  - [ ] Test API key stored via credentials.set, not in config JSON
  - [ ] Test GET returns masked key (never full key)

## Dev Notes

### API key masking

Never return a full API key in the GET response. Return `null` if not set, or a masked version: show first 3 and last 3 characters, mask the rest:

```python
def mask_key(key: str) -> str:
    if len(key) <= 6: return "***"
    return key[:3] + "..." + key[-3:]
```

### API key storage location

BYOK API keys go into the OS keychain via `credentials.set()`. They do NOT go into `data/settings.json`. The settings endpoint writes keys to keychain and reads them back (masked) for display.

### Test connection implementation

```python
@router.post("/settings/llm/test")
async def test_llm_connection(config: AppConfig = Depends(get_config)):
    try:
        response = await llm.complete("Say OK in one word.", config)
        return {"data": {"connected": True, "response": response[:50]}}
    except StageError as e:
        return {"data": {"connected": False, "error": str(e)}}
```

### MCP Sampling in Settings

Show MCP Sampling as an option with a note: "Available when running via Claude Desktop or Hermes MCP." No API key field shown for this provider. Test connection returns "Connected if running in MCP context, otherwise falls back to Ollama."

### References

- [Source: docs/ARCHITECTURE.md § "Authentication & Security — keyring namespace"] — key names
- [Source: docs/epics-stories.md § "Story 8.6"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
