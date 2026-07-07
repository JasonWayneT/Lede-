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
| `FR-006` | functional | P0 | superseded | Each Cluster is assigned to a user-configured Section; unmatched Clusters go to "Other". | `AC-012` | `BMAD-SRC-002` | PRD §4.2 FR-6. Superseded by `FR-032` via `CR-007` (2026-07-06) — no longer describes system behavior. |
| `FR-007` | functional | P0 | accepted | System frames each Cluster with depth tier, lead angle, stakes, and guardrails before drafting. | `AC-013` | `BMAD-SRC-002` | PRD §4.2 FR-7 |
| `FR-008` | functional | P0 | accepted | System generates one editorial Story per Cluster as broadcast-style prose, with source attribution, respecting depth tier. | `AC-014` | `BMAD-SRC-002` | PRD §4.2 FR-7a |
| `FR-009` | functional | P0 | accepted | System assembles all Stories into a dated Briefing document organized by Section with header metadata. | `AC-015` | `BMAD-SRC-002` | PRD §4.2 FR-8 |
| `FR-010` | functional | P0 | accepted | System rewrites assembled Briefing prose into a TTS-optimized narration script and pronunciation guide. | `AC-016` | `BMAD-SRC-002` | PRD §4.3 FR-9 |
| `FR-011` | functional | P0 | accepted | System generates an audio file from the TTS script; audio failure is non-fatal to the Run. | `AC-017` | `BMAD-SRC-002` | PRD §4.3 FR-10 |
| `FR-012` | functional | P1 | accepted | User can select/configure TTS engine in Settings and run a test voice. | `AC-018` | `BMAD-SRC-002` | PRD §4.3 FR-11 |
| `FR-013` | functional | P0 | accepted | System validates the Briefing package via deterministic QA checks before completion. | `AC-019`, `AC-091` | `BMAD-SRC-002` | PRD §4.4 FR-12. Note (`CR-007`, 2026-07-06): Check 1 no longer requires per-Section story coverage — see `AC-091` and `7-3-qa-gate-stage.md`. |
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
| `BUG-001` | bug | P0 | verified | `_ollama_complete` never set `options.num_ctx`, silently capping every Ollama request at Ollama's 2048-token default regardless of the configured model's real context window. | `AC-056` | `docs/spec/09-known-issues/BUG-001.md` | Fixed via `CR-001`; see `ADR-001`. |
| `ARCH-006` | architecture | P0 | verified | Provide `AppConfig.ollama_num_ctx` set explicitly on every Ollama request, and one shared per-source text budget used identically by frame and draft stages (replacing independent 300/500-char truncations). | `AC-057` | `docs/spec/07-decisions/ADR-001.md` | Implemented via `CR-001`. |
| `FR-027` | functional | P1 | verified | Before a source's text is used to frame or draft a story, if it exceeds the shared per-source budget the system extracts explicit facts from it in sentence-aligned chunks (map step, no inference) and uses the concatenated facts in place of the raw text; sources under budget pass through unmodified. | `AC-058..AC-060` | `docs/spec/03-feature-specs/5-4-condense-long-sources.md` | Implemented via `CR-001`; see `ADR-001`. |
| `BUG-002` | bug | P2 | verified | `tests/api/test_settings.py` sent JSON bodies to `gmail`/`schedule`/`tts` PUT routes that were intentionally switched to `Form(...)` parameters to match the real htmx-form UI, so posted values (and invalid values) never reached the routes. | `AC-061..AC-064` | `docs/spec/09-known-issues/BUG-002.md` | Fixed via `CR-002`; test-only fix. |
| `BUG-003` | bug | P2 | verified | `tests/services/test_gmail.py` exercised `gmail.authorize()`/`InstalledAppFlow`, removed by the OAuth redirect-flow refactor (`6e0a3dd`) that replaced the blocking local-server flow with `build_auth_url()`/`exchange_code()`. | `AC-065` | `docs/spec/09-known-issues/BUG-003.md` | Fixed via `CR-002`; test-only fix. |
| `BUG-004` | bug | P3 | verified | `tests/test_config.py::test_app_config_defaults` asserted a stale `ollama_model_name` default (`"llama3.2"`) after the default was intentionally upgraded to `"qwen2.5:7b-instruct-q4_K_M"` in `b2626a4`. | `AC-066` | `docs/spec/09-known-issues/BUG-004.md` | Fixed via `CR-002`; test-only fix. |
| `FR-028` | functional | P2 | verified | Frame stage additionally classifies each story's `sensitivity` (`normal|serious|sensitive|crisis`) and `story_weight` (`light|medium|heavy|sensitive`) in its existing structured-output call, for later use by music selection/mixing (Music Roadmap Phase 3/5). | `AC-067..AC-069` | `docs/spec/03-feature-specs/5-5-music-classification.md` | Implemented via `CR-003`; see `ADR-002` for why only these two fields (not the original four). |
| `FR-029` | functional | P2 | verified | System deterministically selects a music style and voice-safe asset per drafted story from `section_name` + `sensitivity` (segment-role override takes priority; sensitive/crisis content gets no music; unmapped sections fall back to a safe default). | `AC-070..AC-073` | `docs/spec/03-feature-specs/5-6-music-selection.md` | Implemented via `CR-004`; see `ADR-003`. |
| `BUG-005` | bug | P1 | verified | `tts_prep` built its prompt from `packet.assembled_markdown`, which is written only by the later `assemble` stage — so narration was generated from an empty string. | `AC-074` | `docs/spec/09-known-issues/BUG-005.md` | Fixed via `CR-005` by deriving narration from `drafted_stories`; see `ADR-004`. |
| `FR-030` | functional | P2 | verified | Audio is synthesized from an ordered plan of discrete segments (intro, per-story with section transitions between sections, outro) with known per-segment durations, concatenated into the single `briefing.mp3`; `selected_music` is threaded onto every segment for later mixing. | `AC-074..AC-079` | `docs/spec/03-feature-specs/6-4-audio-segment-plan.md` | Implemented via `CR-005`; see `ADR-004`. Structural segments are music-only placeholders until Phase 5 mixing. |
| `FR-031` | functional | P2 | verified | Audio mixing lays a ducked, looped, faded music bed under each story's narration (by `story_weight` profile) and renders the intro/outro/section-transition music-only stingers, into the single 44.1 kHz stereo `briefing.mp3`; no-music and missing-file cases degrade to dry voice, non-fatally. | `AC-080..AC-085` | `docs/spec/03-feature-specs/6-5-audio-mixing.md` | Implemented via `CR-006`; see `ADR-005`. numpy + scipy + soundfile, no new dependency. |
| `BUG-006` | bug | P1 | verified | Dashboard only checked for `status == "running"`, never `"hold"` — a failed run (e.g. Ollama unreachable) was invisible on the main landing page even though History already tracked and displayed it. | `AC-086` | `docs/spec/09-known-issues/BUG-006.md` | Fixed directly (lightweight bug-fix workflow, no CR). |
| `BUG-007` | bug | P2 | verified (partial — see notes) | Music clips measured a ~15dB crest factor uncompensated by the flat `duck_db` gain, so transients could poke through under narration, worse when a clip looped under a long story; `_loop_to_length` had no crossfade at the repeat seam; `_moving_average` zero-padded at boundaries, falsely dipping gain near clip edges. | `AC-087..AC-089` | `docs/spec/09-known-issues/BUG-007.md` | Fixed directly. Whether to also deepen `duck_db` further is an open, ear-judged tradeoff — see `BUG-007.md` Open risk. |
| `FR-032` | functional | P2 | verified | Select stage assigns each Cluster a freeform, LLM-generated section name (1-3 words, Title Case) instead of classifying against `config.sections`; falls back to "Other" for thin/unclear content or names over 3 words. Interim behavior — supersedes `FR-006` pending a real topic taxonomy once enough runs accumulate to aggregate one. | `AC-090` | `docs/spec/05-change-requests/CR-007.md` | Retroactive doc — code shipped ahead of spec; formalized via `CR-007` (2026-07-06). See `4-6-select-stage.md`. |
| `FR-033` | functional | P2 | verified | User can paste one or more YouTube URLs; system extracts each video's transcript via `youtube_transcript_api`, skipping URLs with no transcript or under 100 words. | `AC-092..AC-093` | `docs/spec/05-change-requests/CR-008.md` | Retroactive doc — code shipped ahead of spec; formalized via `CR-008` (2026-07-06). See `13-1-youtube-transcript-ingest.md`. PRD §4.8 FR-26. |
| `FR-034` | functional | P2 | verified | User can paste one or more article URLs; system extracts body text via `trafilatura`, falling back to Jina Reader when trafilatura returns under 200 words. | `AC-094` | `docs/spec/05-change-requests/CR-008.md` | Retroactive doc — code shipped ahead of spec; formalized via `CR-008` (2026-07-06). See `13-2-article-url-ingest.md`. PRD §4.8 FR-27. SSRF hardening tracked under `CR-009`/`BUG-008`. |
| `FR-035` | functional | P2 | verified | `POST /api/briefings/on-demand` accepts a URL list + source type, extracts content synchronously, then runs the pipeline from `embed` onward (skipping `ingest`/`extract`) via `run_pipeline_on_demand`, sharing the same retry/Hold/SSE machinery as scheduled/manual runs. | `AC-095` | `docs/spec/05-change-requests/CR-008.md` | Retroactive doc — code shipped ahead of spec; formalized via `CR-008` (2026-07-06). See `13-3-on-demand-ingest-ui-and-api.md`. PRD §4.8 FR-28. |
| `BUG-008` | bug | P1 | verified | Article ingest (`app/services/article.py`) fetched arbitrary user-supplied URLs with no protection against SSRF — no scheme restriction, no check against loopback/private/link-local/reserved addresses. | `AC-096..AC-097` | `docs/spec/09-known-issues/BUG-008.md` | Fixed via `CR-009`. |
| `BUG-009` | bug | P1 | verified | Depth and LLM Provider settings forms in `settings.html` submit as HTML forms; `update_depth`/`update_llm` expected JSON bodies — a `BUG-002`-class recurrence that silently broke saving from the real UI. | `AC-098..AC-099` | `docs/spec/09-known-issues/BUG-009.md` | Fixed via `CR-010`. |
| `BUG-010` | bug | P1 | verified | `_lookback_query` silently swallowed all errors parsing `data/settings.json`, defaulting to 7 days with no log; `get_credentials_path` raised a raw `FileNotFoundError` instead of `StageError`, reachable mid-OAuth-flow. | `AC-100..AC-102` | `docs/spec/09-known-issues/BUG-010.md` | Fixed via `CR-011`. |
| `BUG-011` | bug | P1 | verified | `GET /api/briefings/missed` was a hardcoded stub always returning `missed_at: None`; the dashboard never surfaced a missed-run banner despite Story 9.3 AC-1 requiring one — the retry fired silently with no user-visible signal. | `AC-103..AC-104` | `docs/spec/09-known-issues/BUG-011.md` | Fixed via `CR-012`. |
| `BUG-012` | bug | P2 | verified | A duplicate `email_id` at Run finalization would violate the `processed_emails` unique constraint and roll back the whole commit, failing the Run over one already-processed email. | n/a | `docs/spec/09-known-issues/BUG-012.md` | Fixed via `CR-013`. |
| `BUG-013` | bug | P2 | verified | Malformed/unreadable `music_assets.json` crashed the `draft`/`tts_prep` stages uncaught, instead of degrading to no-music like the missing-file case. | `AC-105..AC-106` | `docs/spec/09-known-issues/BUG-013.md` | Fixed via `CR-013`. |
| `BUG-014` | bug | P2 | verified | A corrupt/zero-length music file raised uncaught in `_load_music`, taking out audio for the entire briefing rather than just the one segment. | `AC-107..AC-108` | `docs/spec/09-known-issues/BUG-014.md` | Fixed via `CR-013`. |
| `BUG-015` | bug | P2 | verified | Check-then-act race between the active-run check and Run insert in `POST /api/briefings` and `/api/briefings/on-demand` could let two near-simultaneous triggers both start; check also missed the "pending" window. | `AC-109` | `docs/spec/09-known-issues/BUG-015.md` | Fixed via `CR-013`. |
| `BUG-016` | bug | P2 | verified | Gemini auth errors classified by lowercased substring matching instead of typed SDK exceptions — fragile against unrelated errors or SDK wording changes. | `AC-110..AC-111` | `docs/spec/09-known-issues/BUG-016.md` | Fixed via `CR-013`. |
| `BUG-017` | bug | P2 | verified | No cap on the number of URLs accepted by `POST /api/briefings/on-demand` — an unbounded list processed sequentially could block a request for a long time. | `AC-112` | `docs/spec/09-known-issues/BUG-017.md` | Fixed via `CR-013`. |
| `BUG-018` | bug | P2 | verified | The retry/resume path (`briefings.retry_run`'s `_resume`) never recorded `ProcessedEmail` rows on successful completion, letting the next run re-fetch and reprocess the same emails. | `AC-113` | `docs/spec/09-known-issues/BUG-018.md` | Fixed via `CR-013`. |

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

| `AC-056` | `BUG-001` | num_ctx sent to Ollama | `config.ollama_num_ctx` default (8192) | `llm.complete()` routes to Ollama | Request body's `options.num_ctx == 8192` | verified |
| `AC-057` | `ARCH-006` | Shared budget used identically | Frame and draft stages both build prompts from the same cluster | Both stages request source text | Both call the same `condense` budget/helper — no independent truncation length | verified |
| `AC-058` | `FR-027` | Under-budget passthrough | Source text length <= `SOURCE_TEXT_BUDGET_CHARS` | Condensation runs | Text returned unchanged; no LLM call made | verified |
| `AC-059` | `FR-027` | Sentence-boundary chunking | Source text length > `SOURCE_TEXT_BUDGET_CHARS` | Condensation splits it into chunks | Each chunk boundary falls on a sentence boundary; no chunk ends mid-sentence | verified |
| `AC-060` | `FR-027` | One condensation pass shared | Frame stage computes `source_texts` for a cluster | Draft stage runs on the same framed story | Draft reads `story["source_texts"]` directly; no second condensation call for the same source | verified |

| `AC-061` | `BUG-002` | Gmail label persists (form-encoded) | Form-encoded body `{"label": "My Newsletters"}` | `PUT /api/settings/gmail` | Response `data.label == "My Newsletters"` | verified |
| `AC-062` | `BUG-002` | Invalid cadence rejected (form-encoded) | Form-encoded body `{"cadence": "hourly", "time": "07:00"}` | `PUT /api/settings/schedule` | Response status `400` | verified |
| `AC-063` | `BUG-002` | Orpheus without CUDA rejected (form-encoded) | Form-encoded body `{"engine": "orpheus"}`, CUDA unavailable | `PUT /api/settings/tts` | Response status `400` with `"CUDA"` in detail | verified |
| `AC-064` | `BUG-002` | Invalid TTS engine rejected (form-encoded) | Form-encoded body `{"engine": "coqui"}` | `PUT /api/settings/tts` | Response status `400` | verified |
| `AC-065` | `BUG-003` | Token stored via exchange_code | Mocked `Flow.from_client_secrets_file(...).fetch_token(...)` | `gmail.exchange_code(code, state, config)` | `credential_store.set(GMAIL_OAUTH_TOKEN, creds.to_json())` called once | verified |
| `AC-066` | `BUG-004` | Config default matches shipped model | No env override for `OLLAMA_MODEL_NAME` | Instantiate `AppConfig()` | `config.ollama_model_name == "qwen2.5:7b-instruct-q4_K_M"` | verified |

| `AC-067` | `FR-028` | Sensitivity classified | Valid LLM JSON with `sensitivity` in `normal|serious|sensitive|crisis` | Frame stage runs | Framed story's `sensitivity` matches the LLM value | verified |
| `AC-068` | `FR-028` | Story weight classified | Valid LLM JSON with `story_weight` in `light|medium|heavy|sensitive` | Frame stage runs | Framed story's `story_weight` matches the LLM value | verified |
| `AC-069` | `FR-028` | Invalid values default safely | LLM returns an out-of-enum or missing `sensitivity`/`story_weight` | Frame stage parses the response | `sensitivity` defaults to `normal`, `story_weight` defaults to `medium`; invalid value is not passed through | verified |

| `AC-070` | `FR-029` | Role override wins | `segment_role` is `intro`, `outro`, or `section_transition` | `select_style()` is called | Returns the fixed role style regardless of `section_name`/`sensitivity` | verified |
| `AC-071` | `FR-029` | Sensitivity gate | `segment_role="main_summary"`, `sensitivity` is `sensitive` or `crisis` | `select_style()` is called | Returns `None` (no music) regardless of `section_name` | verified |
| `AC-072` | `FR-029` | Section mapping + fallback | `segment_role="main_summary"`, `sensitivity="normal"` | `select_style()` is called | Known sections map to their configured style; unmapped sections fall back to `warm_daily_briefing` | verified |
| `AC-073` | `FR-029` | No voice-safe asset | A style has no matching asset, or none are `voice_safe` | `select_asset()` is called | Returns `None`; logs a warning, does not raise | verified |

| `AC-074` | `BUG-005` | Narration from drafted stories | Packet with `drafted_stories` populated, `assembled_markdown` empty | `tts_prep.run()` executes | Segment plan / `tts_script` contains the story prose, not empty-input output | verified |
| `AC-075` | `FR-030` | Segment plan order | Drafted stories across multiple sections | `tts_prep.run()` builds the plan | Order is `intro`, then sections (a `section_transition` before each section after the first), then `outro`; sections ordered per config with `Other` last | verified |
| `AC-076` | `FR-030` | Story segment content | A drafted story with a `> Sources:` trailer and `selected_music` | Plan is built | Its `main_summary` segment's `text` is the prose with the Sources trailer stripped, and carries the story's `selected_music` | verified |
| `AC-077` | `FR-030` | Structural segments music-only | Intro/outro/section_transition segments | Plan is built | They have empty narration `text` and a `selected_music` resolved via the matching `segment_role` (role override) | verified |
| `AC-078` | `FR-030` | Durations + single file | A plan with narrated segments | `synthesize_plan()` runs | Each narrated segment gets a `duration_seconds`; one `briefing.mp3` is written | verified |
| `AC-079` | `FR-030` | Pronunciation non-fatal | Pronunciation-guide LLM call raises/returns unparseable | `tts_prep.run()` executes | Guide is empty, the segment plan is still built, stage does not fail | verified |

| `AC-080` | `FR-031` | Story bed mixed under voice | A narrated story segment with `selected_music` and a `story_weight` | `mix_story()` runs | Music is ducked (below voice), looped to the narration length, faded, and summed with the voice | verified |
| `AC-081` | `FR-031` | Structural stinger rendered | An intro/outro/section_transition segment with `selected_music` | `mix_structural()` runs | A faded music-only clip of the role profile's duration is produced | verified |
| `AC-082` | `FR-031` | No-music → dry voice | A story segment with `selected_music=None` | `mix_story()` runs | Output is the narration alone (resampled to target format), no bed | verified |
| `AC-083` | `FR-031` | Missing file non-fatal | `selected_music` whose file is absent on disk | mixing loads music | Falls back to dry voice (story) / no segment (structural), logs a warning, does not raise | verified |
| `AC-084` | `FR-031` | Format + clip guard | Any mixed segment | mixing completes | Samples are 44.1 kHz stereo and peak magnitude <= ~0.99 | verified |
| `AC-085` | `FR-031` | story_weight selects profile | A story segment carrying `story_weight` | `mix_story()` runs | The mix profile matching that weight is applied (distinct duck/fade from other weights) | verified |

| `AC-086` | `BUG-006` | Hold state surfaced on dashboard | A run exists with `status == "hold"` and an `error` message | Dashboard route renders | Response context includes that run's id/error; rendered HTML contains a hold banner with the error text and a retry control | verified |

| `AC-087` | `BUG-007` | Transient tamed, quiet preserved | A signal with a brief high-amplitude transient far above its own RMS | `_compress_transients()` runs | Transient peak reduced; a quiet region far from the transient is materially unchanged (within 5%) | verified |
| `AC-088` | `BUG-007` | Seamless loop | A clip shorter than the target length | `_loop_to_length()` runs | Repeat-boundary sample jump is no larger than ordinary adjacent-sample variation elsewhere in the signal | verified |
| `AC-089` | `BUG-007` | No edge-padding artifact | Any signal | `_moving_average()` runs | First/last `window/2` samples are not pulled toward zero by boundary zero-padding | verified |

| `AC-090` | `FR-032` | Freeform section naming + fallback | LLM response is empty, over 3 words, or a clean 1-3 word phrase | `select.py` cleans the response | Empty/over-3-words → `"Other"`; otherwise Title-Cased 1-3 word name is used verbatim | verified |
| `AC-091` | `FR-013` | QA gate Check 1 revised | `packet.drafted_stories` is non-empty but does not cover every configured Section | `qa_gate.run()` executes | No failure raised for uneven section coverage; only a fully empty `drafted_stories` list raises | verified |
| `AC-092` | `FR-033` | Video ID extraction | A `youtube.com/watch?v=`, `youtube.com/shorts/`, or `youtu.be/` URL | `_extract_video_id()` runs | 11-char video ID extracted; other shapes return `None` | verified |
| `AC-093` | `FR-033` | Min-word transcript filter | A fetched transcript under 100 words | `fetch_transcript()` runs | Returns `None` with a `WARNING` log; not included in `fetch_transcripts()` output | verified |
| `AC-094` | `FR-034` | trafilatura → Jina fallback | trafilatura returns under 200 words or no result | `fetch_article()` runs | Falls back to Jina Reader; returns `None` if both are insufficient/fail | verified |
| `AC-095` | `FR-035` | On-demand endpoint gating | Empty `urls`, invalid `source_type`, a run already `"running"`, or zero extractable URLs | `POST /api/briefings/on-demand` | Responds `422`/`409` accordingly; no `Run` row created unless extraction yields usable content | verified |
| `AC-096` | `BUG-008` | Unsafe URLs rejected | A URL with a non-http(s) scheme, or resolving to loopback/private/link-local/multicast/reserved | `_is_url_safe_to_fetch()` runs | Returns `False`; `fetch_article()` returns `None` without calling either extractor | verified |
| `AC-097` | `BUG-008` | Fails open on unresolvable/slow DNS | A hostname that doesn't resolve, or DNS resolution exceeds the timeout | `_is_url_safe_to_fetch()` runs | Returns `True` — treated as an ordinary fetch failure downstream, not a security block | verified |
| `AC-098` | `BUG-009` | Depth form-encoded save | Form-encoded body `{"briefing_depth": "deep"}` | `PUT /api/settings/depth` | Response `data.briefing_depth == "deep"`; a JSON body instead returns `422` | verified |
| `AC-099` | `BUG-009` | LLM form-encoded save | Form-encoded body `{"provider": "openai", "api_key": "..."}` | `PUT /api/settings/llm` | API key stored via `credentials.set`; invalid provider value returns `400` | verified |
| `AC-100` | `BUG-010` | Missing credentials.json surfaces as StageError | `get_credentials_path` raises `FileNotFoundError` | `build_auth_url()` / `exchange_code()` runs | `StageError(retryable=False, code=AUTH_ERROR)` raised, not a raw exception | verified |
| `AC-101` | `BUG-010` | Corrupt settings.json logged | `data/settings.json` contains invalid JSON | `_lookback_query()` runs | A `WARNING` is logged; function still returns a valid 7-day-default query | verified |
| `AC-102` | `BUG-010` | Valid lookback setting applied | `data/settings.json` has `lookback_days: 14` | `_lookback_query()` runs | Returned query reflects a 14-day cutoff, not the default | verified |
| `AC-103` | `BUG-011` | Missed-run endpoint reports real state | A missed run is detected by `check_missed_runs` | `GET /api/briefings/missed` | Returns the real `missed_at` timestamp and whether a Run is currently active (`retrying`) | verified |
| `AC-104` | `BUG-011` | Dashboard renders missed-run banner | `missed_run` context is set on the dashboard route | `GET /` renders `dashboard.html` | Banner text "Missed run at {time} — retrying now" (or "not started yet") appears | verified |
| `AC-105` | `BUG-013` | Malformed music registry degrades gracefully | `music_assets.json` contains invalid JSON | `load_music_assets()` runs | Returns `[]` with a `WARNING` log, no exception | verified |
| `AC-106` | `BUG-013` | Unreadable music registry degrades gracefully | `music_assets.json` read raises `OSError` | `load_music_assets()` runs | Returns `[]` with a `WARNING` log, no exception | verified |
| `AC-107` | `BUG-014` | Corrupt music file — story segment | A music file exists but is not valid audio | `mix_story()` runs | Falls back to dry voice, no exception | verified |
| `AC-108` | `BUG-014` | Corrupt music file — structural segment | Same, for `mix_structural()` | `mix_structural()` runs | Returns `None`, no exception | verified |
| `AC-109` | `BUG-015` | Pending run also blocks a second trigger | A Run with `status="pending"` exists | `POST /api/briefings` | Responds `409`, not just for `"running"` | verified |
| `AC-110` | `BUG-016` | Gemini PermissionDenied classified as auth error | `google.api_core.exceptions.PermissionDenied` raised | `_gemini_complete()` runs | `StageError(code=AUTH_ERROR, retryable=False)` raised | verified |
| `AC-111` | `BUG-016` | Unrelated Gemini error not misclassified | A generic exception whose message happens to contain old trigger words | `_gemini_complete()` runs | `StageError(code=PROVIDER_UNAVAILABLE, retryable=True)` raised | verified |
| `AC-112` | `BUG-017` | On-demand URL count capped | More than 10 URLs submitted | `POST /api/briefings/on-demand` | Responds `422` before any extraction begins | verified |
| `AC-113` | `BUG-018` | Retry persists processed emails | A held Run is retried and completes successfully | `retry_run`'s `_resume` finalizes | `ProcessedEmail` rows exist for the run's `emails` | verified |

## Requirement lifecycle notes

- Never reuse deprecated IDs.
- If a requirement changes meaning, create a new ID and mark the old one superseded.
- If a requirement is split, create child IDs and update traceability.
- If a requirement is merged, preserve all old IDs as superseded aliases.

