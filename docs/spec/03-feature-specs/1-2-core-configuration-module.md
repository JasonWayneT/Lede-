# Story 1.2: Core Configuration Module

Status: ready-for-dev

## Story

As a developer,
I want AppConfig to load all application settings from environment variables and provide a validated llm_provider enum,
so that all modules can access typed configuration without reading env vars directly.

## Acceptance Criteria

1. **Given** a `.env` file with `BRIEFING_DATA_DIR` set, **When** `AppConfig` is instantiated, **Then** `config.data_dir` resolves to the configured path and defaults apply for all unset variables

2. **Given** `AppConfig` instantiated with defaults, **When** I read `config.llm_provider`, **Then** it defaults to `"ollama"` and accepts values: `ollama`, `openai`, `anthropic`, `gemini`, `mcp_sampling`

3. **Given** `AppConfig` with an invalid `llm_provider` value, **When** I instantiate `AppConfig`, **Then** a clear `ValidationError` is raised naming the invalid value and listing valid options

4. **Given** `AppConfig`, **When** I read `config.log_level`, **Then** it defaults to `"INFO"` and accepts `DEBUG`, `INFO`, `WARNING`, `ERROR`

5. **Given** `AppConfig`, **When** I read `config.briefing_depth`, **Then** it defaults to `"standard"` and accepts `"brief"`, `"standard"`, `"deep"`

6. **Given** a pipeline stage receiving config as a parameter, **When** I inspect the stage file, **Then** no direct `os.environ` or `os.getenv` calls appear — all settings are read from config

## Tasks / Subtasks

- [ ] Implement `AppConfig` in `app/core/config.py` (AC: 1, 2, 3, 4, 5)
  - [ ] Use `pydantic-settings` (included via `fastapi` dependency) or plain dataclass with `python-dotenv` — prefer pydantic `BaseSettings` for built-in env loading and validation
  - [ ] Add field: `data_dir: Path` — reads from `BRIEFING_DATA_DIR`, defaults to `./data`
  - [ ] Add field: `log_level: str` — reads from `LOG_LEVEL`, defaults to `"INFO"`, validator for `DEBUG|INFO|WARNING|ERROR`
  - [ ] Add field: `llm_provider: str` — reads from `LLM_PROVIDER`, defaults to `"ollama"`, validator enforcing `ollama|openai|anthropic|gemini|mcp_sampling`
  - [ ] Add field: `briefing_depth: str` — reads from `BRIEFING_DEPTH`, defaults to `"standard"`, validator enforcing `brief|standard|deep`
  - [ ] Add field: `ollama_model_name: str` — reads from `OLLAMA_MODEL_NAME`, defaults to `"llama3.2"`
  - [ ] Add field: `ollama_base_url: str` — reads from `OLLAMA_BASE_URL`, defaults to `"http://localhost:11434"`
  - [ ] Add field: `similarity_threshold: float` — reads from `SIMILARITY_THRESHOLD`, defaults to `0.75` (used by cluster stage)
  - [ ] Add field: `gmail_label: str` — reads from `GMAIL_LABEL`, defaults to `"Newsletters"`
  - [ ] Add field: `sections: list[str]` — reads from `BRIEFING_SECTIONS` as comma-separated, defaults to `["AI", "Technology", "Finance", "Politics", "Other"]`
  - [ ] Validation error messages must name the invalid value and list all valid options (AC: 3)

- [ ] Add `.env.example` entries for all new fields (AC: 6)
  - [ ] Add commented example lines for `LLM_PROVIDER`, `BRIEFING_DEPTH`, `OLLAMA_MODEL_NAME`, `OLLAMA_BASE_URL`, `SIMILARITY_THRESHOLD`, `GMAIL_LABEL`, `BRIEFING_SECTIONS`

- [ ] Write tests in `tests/api/test_settings.py` or create `tests/test_config.py` (AC: 1–5)
  - [ ] Test default values when no env vars set
  - [ ] Test valid `llm_provider` values all accepted
  - [ ] Test invalid `llm_provider` raises `ValidationError` with descriptive message
  - [ ] Test `briefing_depth` validation
  - [ ] Test `log_level` validation

## Dev Notes

### Library choice

Use `pydantic-settings` (`from pydantic_settings import BaseSettings`). It is already transitively available since FastAPI depends on Pydantic v2. No additional `uv add` needed. Pattern:

```python
from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path

class AppConfig(BaseSettings):
    data_dir: Path = Path("./data")
    log_level: str = "INFO"
    llm_provider: str = "ollama"
    briefing_depth: str = "standard"
    ...

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, v):
        valid = {"ollama", "openai", "anthropic", "gemini", "mcp_sampling"}
        if v not in valid:
            raise ValueError(f"Invalid llm_provider '{v}'. Must be one of: {sorted(valid)}")
        return v
```

### No singleton

Do NOT create a module-level singleton `config = AppConfig()`. Config is passed as a parameter into every stage and service. Entry points (`main.py`, `mcp_server.py`) instantiate it and inject it. This avoids hidden global state and makes testing trivial (pass a test AppConfig).

### Entry point isolation

`config.py` imports only from Python stdlib and pydantic. It must not import from `api/`, `pipeline/`, `services/`, or `db/`.

### sections field

`BRIEFING_SECTIONS` is comma-separated in the env var: `"AI,Technology,Finance"`. Parse in validator. "Other" is always appended if not present — it is the immutable catch-all section.

### References

- [Source: docs/ARCHITECTURE.md § "Implementation Patterns — LLM Provider Routing"] — provider enum values
- [Source: docs/ARCHITECTURE.md § "Implementation Patterns — Naming Patterns"] — UPPER_SNAKE_CASE for constants
- [Source: docs/epics-stories.md § "Story 1.2"] — acceptance criteria
- [Source: docs/epics-stories.md § "Additional Requirements"] — `mcp_sampling` is the 5th provider

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implemented `AppConfig` using `pydantic-settings` with explicit env aliases (`BRIEFING_DATA_DIR`, `BRIEFING_SECTIONS`) and validators for `llm_provider`, `log_level`, and `briefing_depth`.
- Implemented comma-separated `BRIEFING_SECTIONS` parsing with mandatory `"Other"` append; disabled pydantic-settings env JSON decoding to allow CSV input.
- Updated `briefing/.env.example` with commented entries for all Story 1.2 fields.
- Verification: `uv run pytest -q tests/test_config.py` (PASS).

### File List

- `briefing/app/core/config.py`
- `briefing/.env.example`
- `briefing/tests/test_config.py`
