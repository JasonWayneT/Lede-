# Requirements Registry

This is the canonical list of project requirements. Feature specs, tasks, tests, and code changes must trace back here.

## ID naming convention

Use only the categories the project needs.

| Prefix | Category | Example |
|---|---|---|
| `FR` | Functional requirement | `FR-001` |
| `NFR` | Non-functional requirement | `NFR-001` |
| `UX` | User experience requirement | `UX-001` |
| `DES` | Visual or interaction design requirement | `DES-001` |
| `ARCH` | Architecture requirement | `ARCH-001` |
| `DATA` | Data requirement | `DATA-001` |
| `SEC` | Security/privacy requirement | `SEC-001` |
| `INT` | Integration requirement | `INT-001` |
| `OPS` | Operations requirement | `OPS-001` |
| `AC` | Acceptance criterion | `AC-001` |
| `TEST` | Test case | `TEST-001` |
| `BUG` | Known bug or regression | `BUG-001` |
| `ADR` | Architecture decision | `ADR-001` |
| `CR` | Change request | `CR-001` |

## Status values

- `draft`: proposed but not accepted
- `accepted`: approved source of truth
- `implemented`: implemented in code
- `verified`: implemented and validated
- `deprecated`: no longer active
- `superseded`: replaced by another ID

## Requirement records

| ID | Type | Priority | Status | Requirement | Acceptance criteria | Source | Notes |
|---|---|---|---|---|---|---|---|
| `ARCH-001` | architecture | P0 | verified | Scaffold the `briefing/` uv project directory structure and dependency set so feature work can proceed without setup decisions. | `AC-001..AC-006` | `docs/spec/03-feature-specs/1-1-scaffold-project-structure.md` | Verified via `TEST-001` + direct `uv run` import check and path existence check. |
| `TASK-001` | task | P0 | verified | Implement Story 1.1 scaffold (initialize uv project, install deps, create full directory tree and file stubs). | `AC-001..AC-006` | `docs/spec/03-feature-specs/1-1-scaffold-project-structure.md` | Execution task for `ARCH-001`. |
| `TEST-001` | test | P0 | verified | Verify Story 1.1 scaffold: required paths exist and key imports succeed. |  | `docs/spec/08-test-specs/TEST-001.md` | Manual verification for scaffold-only story. |
| `ARCH-002` | architecture | P0 | verified | Provide `AppConfig` that loads typed settings from env / `.env` with validated enums and defaults. | `AC-033..AC-038` | `docs/spec/03-feature-specs/1-2-core-configuration-module.md` | Implemented with `pydantic-settings` and tests. |
| `TASK-002` | task | P0 | verified | Implement Story 1.2 core configuration module (`AppConfig`) and update `.env.example`. | `AC-033..AC-038` | `docs/spec/03-feature-specs/1-2-core-configuration-module.md` | Execution task for `ARCH-002`. |
| `TEST-002` | test | P0 | verified | Verify Story 1.2 config defaults and validation. |  | `docs/spec/08-test-specs/TEST-002.md` | Automated via `pytest`. |
| `ARCH-003` | architecture | P0 | verified | Provide async SQLite DB models and initialize schema during FastAPI lifespan using `create_all`. | `AC-039..AC-044` | `docs/spec/03-feature-specs/1-3-database-models-and-async-sqlite.md` | DB URL derived from `AppConfig.data_dir`; no Alembic. |
| `TASK-003` | task | P0 | verified | Implement Story 1.3 DB layer (`database.py`, `models.py`) and wire `init_db()` into FastAPI lifespan. | `AC-039..AC-044` | `docs/spec/03-feature-specs/1-3-database-models-and-async-sqlite.md` | Execution task for `ARCH-003`. |
| `TEST-003` | test | P0 | verified | Verify Story 1.3 schema creation, idempotency, and session usability. |  | `docs/spec/08-test-specs/TEST-003.md` | Automated via `pytest-asyncio`. |
| `ARCH-004` | architecture | P0 | verified | Provide centralized OS keychain credential wrapper under keyring service `"briefing"` with defined key constants. | `AC-045..AC-050` | `docs/spec/03-feature-specs/1-4-credential-store-keyring-wrapper.md` | All credential access centralized; tests fully mocked. |
| `TASK-004` | task | P0 | verified | Implement Story 1.4 keyring wrapper (`app/core/credentials.py`) and tests. | `AC-045..AC-050` | `docs/spec/03-feature-specs/1-4-credential-store-keyring-wrapper.md` | Execution task for `ARCH-004`. |
| `TEST-004` | test | P0 | verified | Verify Story 1.4 credential wrapper behavior (mocked keyring). |  | `docs/spec/08-test-specs/TEST-004.md` | Automated via `pytest`. |
| `ARCH-005` | architecture | P0 | verified | Provide `StageError` and error code constants; FastAPI returns standardized error envelope. | `AC-051..AC-055` | `docs/spec/03-feature-specs/1-5-error-types-stageerror.md` | Errors module imports stdlib only. |
| `TASK-005` | task | P0 | verified | Implement Story 1.5 error types/constants and FastAPI exception handler + tests. | `AC-051..AC-055` | `docs/spec/03-feature-specs/1-5-error-types-stageerror.md` | Execution task for `ARCH-005`. |
| `TEST-005` | test | P0 | verified | Verify Story 1.5 error constants, `StageError` behavior, and FastAPI handler envelope. |  | `docs/spec/08-test-specs/TEST-005.md` | Automated via `pytest`. |
| `FR-001` | functional | P0 | verified | User can authorize Gmail access via browser-based OAuth 2.0 during initial setup; token stored locally. | `AC-007` | `BMAD-SRC-002` | Implemented via `services/gmail.authorize()` + `setup.py`. |
| `TASK-006` | task | P0 | verified | Implement Story 2.1 Gmail OAuth authorization + token storage in keyring. | `AC-007` | `docs/spec/03-feature-specs/2-1-gmail-oauth-authorization.md` | Execution task for `FR-001`. |
| `TEST-006` | test | P0 | verified | Verify Gmail OAuth token storage and auth error handling. |  | `docs/spec/08-test-specs/TEST-006.md` | Automated via `pytest`. |
| `FR-002` | functional | P0 | verified | System fetches emails from the configured Gmail label that do not appear in the Processed Log on each Run. | `AC-008` | `BMAD-SRC-002` | Implemented via `services/gmail.fetch_unprocessed_emails(...)`. |
| `TASK-007` | task | P0 | verified | Implement Story 2.2 label-based fetch and processed-id filtering. | `AC-008` | `docs/spec/03-feature-specs/2-2-label-based-email-fetch.md` | Execution task for `FR-002`. |
| `TEST-007` | test | P0 | verified | Verify label-based fetch excludes processed emails and returns required fields. |  | `docs/spec/08-test-specs/TEST-007.md` | Automated via `pytest`. |
| `FR-003` | functional | P0 | verified | After a successful Run, system records processed email IDs; user can clear the log from Settings. | `AC-009` | `BMAD-SRC-002` | Implemented via orchestrator atomic transaction + settings clear endpoint. |
| `TASK-008` | task | P0 | verified | Implement Story 2.3 processed log atomicity helpers and clear endpoint. | `AC-009` | `docs/spec/03-feature-specs/2-3-processed-log-management.md` | Execution task for `FR-003`. |
| `TEST-008` | test | P0 | verified | Verify processed log atomicity and clear endpoint behavior. |  | `docs/spec/08-test-specs/TEST-008.md` | Automated via `pytest-asyncio` + httpx ASGI tests. |
| `FR-004` | functional | P0 | accepted | System extracts plain text, title, sender name, and date from each Newsletter HTML body. | `AC-010` | `BMAD-SRC-002` | PRD §4.2 FR-4 |
| `FR-005` | functional | P0 | accepted | System generates embeddings for extracted chunks and groups them into Clusters using similarity thresholds. | `AC-011` | `BMAD-SRC-002` | PRD §4.2 FR-5 |
| `FR-006` | functional | P0 | accepted | Each Cluster is assigned to a user-configured Section; unmatched Clusters go to "Other". | `AC-012` | `BMAD-SRC-002` | PRD §4.2 FR-6 |
| `FR-007` | functional | P0 | accepted | System frames each Cluster with depth tier, lead angle, stakes, and guardrails before drafting. | `AC-013` | `BMAD-SRC-002` | PRD §4.2 FR-7 |
| `FR-008` | functional | P0 | accepted | System generates one editorial Story per Cluster as broadcast-style prose, with source attribution, respecting depth tier. | `AC-014` | `BMAD-SRC-002` | PRD §4.2 FR-7a |
| `FR-009` | functional | P0 | accepted | System assembles all Stories into a dated Briefing document organized by Section with header metadata. | `AC-015` | `BMAD-SRC-002` | PRD §4.2 FR-8 |
| `FR-010` | functional | P0 | accepted | System rewrites assembled Briefing prose into a TTS-optimized narration script and pronunciation guide. | `AC-016` | `BMAD-SRC-002` | PRD §4.3 FR-9 |
| `FR-011` | functional | P0 | accepted | System generates an audio file from the TTS script; audio failure is non-fatal to the Run. | `AC-017` | `BMAD-SRC-002` | PRD §4.3 FR-10 |
| `FR-012` | functional | P1 | accepted | User can select/configure TTS engine in Settings and run a test voice. | `AC-018` | `BMAD-SRC-002` | PRD §4.3 FR-11 |
| `FR-013` | functional | P0 | accepted | System validates the Briefing package via deterministic QA checks before completion. | `AC-019` | `BMAD-SRC-002` | PRD §4.4 FR-12 |
| `FR-014` | functional | P0 | accepted | System retries failures with a structured policy and can enter a Hold state with manual retry. | `AC-020` | `BMAD-SRC-002` | PRD §4.4 FR-13 |
| `FR-015` | functional | P0 | accepted | System uses a local Ollama instance as the default LLM Provider, with configurable model name. | `AC-021` | `BMAD-SRC-002` | PRD §4.5 FR-14 |
| `FR-016` | functional | P0 | accepted | User can configure a BYOK API key for OpenAI/Anthropic/Gemini; switching providers takes effect next Run without restart. | `AC-022` | `BMAD-SRC-002` | PRD §4.5 FR-15 |
| `FR-017` | functional | P0 | accepted | On first launch, app presents a setup wizard (OAuth required; other steps skippable/revisitable). | `AC-023` | `BMAD-SRC-002` | PRD §4.6 FR-16 |
| `FR-018` | functional | P1 | accepted | User can revisit onboarding configuration from Settings at any time. | `AC-024` | `BMAD-SRC-002` | PRD §4.6 FR-17 |
| `FR-019` | functional | P0 | accepted | User can trigger a Run manually via the UI. | `AC-025` | `BMAD-SRC-002` | PRD §4.7 FR-18 |
| `FR-020` | functional | P0 | accepted | UI displays a real-time pipeline progress log while a Run is active. | `AC-026` | `BMAD-SRC-002` | PRD §4.7 FR-19 |
| `FR-021` | functional | P0 | accepted | UI displays a list of past Briefings with date/story count/section breakdown and download links. | `AC-027` | `BMAD-SRC-002` | PRD §4.7 FR-20 |
| `FR-022` | functional | P1 | accepted | User can configure Gmail label and re-authorize OAuth from Settings. | `AC-028` | `BMAD-SRC-002` | PRD §4.7 FR-21 |
| `FR-023` | functional | P1 | accepted | User can manage Sections (add/rename/remove/reorder) with "Other" catch-all and at least one section required. | `AC-029` | `BMAD-SRC-002` | PRD §4.7 FR-22 |
| `FR-024` | functional | P1 | accepted | User can set default Briefing Depth from Settings. | `AC-030` | `BMAD-SRC-002` | PRD §4.7 FR-23 |
| `FR-025` | functional | P1 | accepted | User can select LLM provider/model and test connection from Settings; keys masked. | `AC-031` | `BMAD-SRC-002` | PRD §4.7 FR-24 |
| `FR-026` | functional | P1 | accepted | User can configure schedule + optional daemon mode; missed runs are detected and retried on next app open. | `AC-032` | `BMAD-SRC-002` | PRD §4.7 FR-25 |
| `NFR-001` | non-functional | P0 | accepted | Async-first: web server must not block on pipeline execution. |  | `BMAD-SRC-002` | PRD NFRs |
| `NFR-002` | non-functional | P0 | accepted | Streaming: live log supports server→browser real-time streaming (SSE). |  | `BMAD-SRC-002` | PRD NFRs |
| `NFR-003` | non-functional | P0 | accepted | Local-first security: OAuth token and API keys encrypted at rest; never transmitted beyond configured provider APIs. |  | `BMAD-SRC-002` | PRD NFRs |
| `NFR-004` | non-functional | P0 | accepted | Partial rerun: handoff artifacts persisted to disk for partial rerun without replaying full run. |  | `BMAD-SRC-002` | PRD NFRs |
| `NFR-005` | non-functional | P1 | accepted | Daemon mode: scheduler can fire runs independently of the web server process. |  | `BMAD-SRC-002` | PRD NFRs |
| `NFR-006` | non-functional | P1 | accepted | Self-contained install: dependencies (incl. Kokoro weights) auto-downloaded during setup. |  | `BMAD-SRC-002` | PRD NFRs |
| `NFR-007` | non-functional | P1 | accepted | Setup time: new technical user completes setup and generates first Briefing in under 15 minutes. |  | `BMAD-SRC-002` | PRD SM-2 |
| `NFR-008` | non-functional | P0 | accepted | Entry point isolation: shared core modules never import from `main.py` or `mcp_server.py`. |  | `BMAD-SRC-003` | Architecture enforcement rule |

## Acceptance criteria

Write acceptance criteria in Given/When/Then form when possible.

| ID | Parent requirement | Scenario | Given | When | Then | Status |
|---|---|---|---|---|---|---|
| `AC-001` | `ARCH-001` | Root files exist | Python 3.11+ and `uv` installed | Initialization per Story 1.1 is run | `briefing/` exists with `pyproject.toml`, `.env.example`, `.gitignore`, `setup.py`, `briefing.sh`, `briefing.bat` | accepted |
| `AC-002` | `ARCH-001` | Directory tree exists | Scaffolded project | Inspect the directory tree | All required directories exist (app/core, app/api, pipeline/stages, services, db, templates; pipeline_prompts/stages; data/{briefings,artifacts}; tests subtrees) | accepted |
| `AC-003` | `ARCH-001` | Imports succeed | Dependencies installed via uv | Run `uv run python -c "import fastapi, sqlalchemy, mcp"` | Command exits 0 | accepted |
| `AC-004` | `ARCH-001` | env template exists | `.env.example` exists | Read `.env.example` | Contains `BRIEFING_DATA_DIR` and `LOG_LEVEL` with example values | accepted |
| `AC-005` | `ARCH-001` | gitignore excludes runtime files | `.gitignore` exists | Read `.gitignore` | Excludes `data/`, `*.db`, `*.log`, `__pycache__/`, `.env`, `*.pyc`, `.venv/` | accepted |
| `AC-006` | `ARCH-001` | prompt placeholders exist | `pipeline_prompts/` exists | Inspect prompt files | `handoff-schema.yaml` exists (empty placeholder) and `stages/` contains `select.md`, `frame.md`, `draft.md`, `tts_prep.md` (empty placeholders) | accepted |

| `AC-007` | `FR-001` | OAuth authorization | User runs onboarding wizard with credentials.json | Authorize Gmail via browser OAuth flow | Token is stored locally via encrypted credential store | accepted |
| `AC-008` | `FR-002` | Label-based fetch | Configured Gmail label and valid token | Ingest runs | Only label-matching, unprocessed emails are fetched | accepted |
| `AC-009` | `FR-003` | Processed log atomicity | A Run completes successfully | Orchestrator finalizes Run | Processed emails are recorded atomically; failed Runs do not record them | accepted |
| `AC-010` | `FR-004` | Extract metadata + text | Newsletter HTML | Extract stage runs | Plain text + title + sender + date extracted | accepted |
| `AC-011` | `FR-005` | Embedding clustering prep | Extracted texts | Embed + cluster runs | Embeddings created and grouped by similarity threshold | accepted |
| `AC-012` | `FR-006` | Section assignment | Clusters + configured sections | Select stage runs | Each cluster assigned exactly one section; unmatched → Other | accepted |
| `AC-013` | `FR-007` | Frame clusters | Selected clusters + depth | Frame stage runs | depth_tier, lead_angle, stakes, guardrails populated | accepted |
| `AC-014` | `FR-008` | Draft stories | Framed clusters | Draft stage runs | One story per cluster, broadcast-style prose with attribution | accepted |
| `AC-015` | `FR-009` | Assemble briefing | Drafted stories + section order | Assemble stage runs | Markdown saved + header metadata present | accepted |
| `AC-016` | `FR-010` | TTS prep script | Assembled markdown | TTS prep runs | Markdown removed; segues + pronunciation guide produced | accepted |
| `AC-017` | `FR-011` | Audio generation non-fatal | TTS script | Audio synth runs | Audio saved when possible; failures degrade gracefully | accepted |
| `AC-018` | `FR-012` | TTS settings/test | Settings UI | Test voice invoked | Sample audio plays in browser | accepted |
| `AC-019` | `FR-013` | QA validation | Assembled package | QA gate runs | Deterministic checks pass/fail and set qa_passed | accepted |
| `AC-020` | `FR-014` | Retry + hold | StageError occurs | Orchestrator retries tiers | Enters hold after tiers; manual retry available | accepted |
| `AC-021` | `FR-015` | Ollama default provider | Ollama running | llm.complete called | Uses Ollama HTTP API; errors surface as StageError | accepted |
| `AC-022` | `FR-016` | BYOK providers | API key saved in credential store | llm.complete called | Uses selected provider; auth errors non-retryable | accepted |
| `AC-023` | `FR-017` | First-run wizard | No token/config | Open app first time | Wizard shown; OAuth required; others skippable | accepted |
| `AC-024` | `FR-018` | Revisit onboarding | Returning user | Open Settings | Setup status shown; items revisitable | accepted |
| `AC-025` | `FR-019` | Run trigger | Dashboard | Click Run Briefing | Run starts and returns run_id | accepted |
| `AC-026` | `FR-020` | Live log | Run active | SSE stream connected | Stage/log events appear in browser | accepted |
| `AC-027` | `FR-021` | History | Completed runs | View history | Entries show date/story count/sections + downloads | accepted |
| `AC-028` | `FR-022` | Gmail settings | Settings page | Save label / reauth | Label persists; OAuth flow available | accepted |
| `AC-029` | `FR-023` | Section mgmt | Settings page | Add/rename/remove/reorder | Changes persist; Other protected; at least one section | accepted |
| `AC-030` | `FR-024` | Depth setting | Settings page | Save depth | Applies next run | accepted |
| `AC-031` | `FR-025` | Provider settings | Settings page | Save provider & test | Connection test works; keys masked | accepted |
| `AC-032` | `FR-026` | Schedule + daemon | Settings page | Save schedule / daemon | Runs schedule; daemon optional; missed run retry | accepted |

| `AC-033` | `ARCH-002` | Config data_dir from env | `.env` sets `BRIEFING_DATA_DIR` | Instantiate `AppConfig` | `data_dir` resolves to configured path and defaults apply for unset fields | verified |
| `AC-034` | `ARCH-002` | llm_provider defaults + allowed values | Defaults | Read `config.llm_provider` | Defaults to `ollama`; accepts `ollama|openai|anthropic|gemini|mcp_sampling` | verified |
| `AC-035` | `ARCH-002` | llm_provider invalid raises | Invalid env value | Instantiate `AppConfig` | Raises `ValidationError` naming invalid value and listing valid options | verified |
| `AC-036` | `ARCH-002` | log_level defaults + allowed values | Defaults | Read `config.log_level` | Defaults to `INFO`; accepts `DEBUG|INFO|WARNING|ERROR` | verified |
| `AC-037` | `ARCH-002` | briefing_depth defaults + allowed values | Defaults | Read `config.briefing_depth` | Defaults to `standard`; accepts `brief|standard|deep` | verified |
| `AC-038` | `ARCH-002` | No env access in stages | Stage receives config parameter | Inspect stage files | No direct `os.environ` or `os.getenv` usage | verified |

| `AC-039` | `ARCH-003` | DB created on startup | App starts first time | FastAPI lifespan runs | `briefing.db` created and tables exist | verified |
| `AC-040` | `ARCH-003` | Runs table schema | DB initialized | Inspect schema | `runs` has columns per Story 1.3 | verified |
| `AC-041` | `ARCH-003` | Briefing outputs schema | DB initialized | Inspect schema | `briefing_outputs` has columns per Story 1.3 | verified |
| `AC-042` | `ARCH-003` | Processed emails schema | DB initialized | Inspect schema | `processed_emails` has columns per Story 1.3 | verified |
| `AC-043` | `ARCH-003` | Session context manager | DB module available | Call `get_session()` | Returns async session usable with `async with` | verified |
| `AC-044` | `ARCH-003` | init_db idempotent | DB exists | Lifespan runs again | No error; data preserved | verified |

| `AC-045` | `ARCH-004` | Store oauth token | Credentials module | Call `set(gmail_oauth_token, ...)` | Stored under `service="briefing"` and username key | verified |
| `AC-046` | `ARCH-004` | Get stored credential | Credential exists | Call `get(...)` | Returns stored string | verified |
| `AC-047` | `ARCH-004` | Get missing returns None | Key unset | Call `get(openai_key)` | Returns `None` | verified |
| `AC-048` | `ARCH-004` | Delete is safe | Key missing or present | Call `delete(anthropic_key)` | Removes entry; missing key does not raise | verified |
| `AC-049` | `ARCH-004` | Constants defined | Inspect module | View constants | Key constants present and exact strings | verified |
| `AC-050` | `ARCH-004` | Cross-platform keychain | Runs on OS | Call credentials ops | Uses OS keychain (via keyring) | verified |

| `AC-051` | `ARCH-005` | StageError carries attributes | Stage raises StageError | Access attributes | `stage_name`, `message`, `retryable` accessible | verified |
| `AC-052` | `ARCH-005` | __str__ formatting | StageError instance | Convert to string | String is `"[stage] message"` | verified |
| `AC-053` | `ARCH-005` | Error code constants exist | Inspect errors module | Read constants | `STAGE_FAILED`, `AUTH_ERROR`, `PROVIDER_UNAVAILABLE`, `VALIDATION_ERROR`, `NOT_FOUND` | verified |
| `AC-054` | `ARCH-005` | Handler returns envelope | StageError reaches app | Exception handler runs | Returns JSON envelope with `error`, `code`, `stage`, `retryable` and HTTP 500 | verified |
| `AC-055` | `ARCH-005` | No circular imports | Shared imports | Import errors module | Imports stdlib only | verified |

## Requirement lifecycle notes

- Never reuse deprecated IDs.
- If a requirement changes meaning, create a new ID and mark the old one superseded.
- If a requirement is split, create child IDs and update traceability.
- If a requirement is merged, preserve all old IDs as superseded aliases.

