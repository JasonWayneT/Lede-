# Traceability Matrix

Use this matrix to prove that each requirement has a spec, task, implementation, and verification path.

## Matrix

| Requirement ID | Source | Feature/design spec | Acceptance criteria | Tasks | Code/modules | Tests | Status |
|---|---|---|---|---|---|---|---|
| `ARCH-001` | `docs/spec/03-feature-specs/1-1-scaffold-project-structure.md` | `docs/spec/03-feature-specs/1-1-scaffold-project-structure.md` | `AC-001..AC-006` | `TASK-001` | `briefing/` scaffold + stubs | `TEST-001` | verified |
| `ARCH-002` | `docs/spec/03-feature-specs/1-2-core-configuration-module.md` | `docs/spec/03-feature-specs/1-2-core-configuration-module.md` | `AC-033..AC-038` | `TASK-002` | `briefing/app/core/config.py` | `TEST-002` | verified |
| `ARCH-003` | `docs/spec/03-feature-specs/1-3-database-models-and-async-sqlite.md` | `docs/spec/03-feature-specs/1-3-database-models-and-async-sqlite.md` | `AC-039..AC-044` | `TASK-003` | `briefing/app/db/{database.py,models.py}`, `briefing/app/main.py` | `TEST-003` | verified |
| `ARCH-004` | `docs/spec/03-feature-specs/1-4-credential-store-keyring-wrapper.md` | `docs/spec/03-feature-specs/1-4-credential-store-keyring-wrapper.md` | `AC-045..AC-050` | `TASK-004` | `briefing/app/core/credentials.py` | `TEST-004` | verified |
| `ARCH-005` | `docs/spec/03-feature-specs/1-5-error-types-stageerror.md` | `docs/spec/03-feature-specs/1-5-error-types-stageerror.md` | `AC-051..AC-055` | `TASK-005` | `briefing/app/core/errors.py`, `briefing/app/main.py` | `TEST-005` | verified |
| `FR-001` | `BMAD-SRC-002` | `docs/spec/03-feature-specs/2-1-gmail-oauth-authorization.md` | `AC-007` | `TASK-006` | `briefing/app/services/gmail.py`, `briefing/setup.py` | `TEST-006` | verified |
| `FR-002` | `BMAD-SRC-002` | `docs/spec/03-feature-specs/2-2-label-based-email-fetch.md` | `AC-008` | `TASK-007` | `briefing/app/services/gmail.py` | `TEST-007` | verified |
| `FR-003` | `BMAD-SRC-002` | `docs/spec/03-feature-specs/2-3-processed-log-management.md` | `AC-009` | `TASK-008` | `briefing/app/pipeline/orchestrator.py`, `briefing/app/api/settings.py`, `briefing/app/services/gmail.py` | `TEST-008` | verified |
| `BUG-001` | `docs/spec/09-known-issues/BUG-001.md` | `docs/spec/07-decisions/ADR-001.md` | `AC-056` | `TASK-009` | `briefing/app/services/llm.py`, `briefing/app/core/config.py` | `TEST-009` | verified |
| `ARCH-006` | `docs/spec/05-change-requests/CR-001.md` | `docs/spec/07-decisions/ADR-001.md` | `AC-057` | `TASK-009`, `TASK-010` | `briefing/app/core/config.py`, `briefing/app/services/llm.py`, `briefing/app/services/condense.py` | `TEST-009`, `TEST-010` | verified |
| `FR-027` | `docs/spec/05-change-requests/CR-001.md` | `docs/spec/03-feature-specs/5-4-condense-long-sources.md` | `AC-058..AC-060` | `TASK-010`, `TASK-011`, `TASK-012` | `briefing/app/services/condense.py`, `briefing/app/pipeline/stages/frame.py`, `briefing/app/pipeline/stages/draft.py`, `briefing/pipeline_prompts/stages/condense.md` | `TEST-010`, `TEST-011` | verified |
| `BUG-002` | `docs/spec/09-known-issues/BUG-002.md` | `docs/spec/03-feature-specs/8-4-settings-gmail-configuration.md`, `8-7-settings-schedule-and-daemon.md`, `6-3-tts-engine-settings.md` | `AC-061..AC-064` | `TASK-015` | `briefing/tests/api/test_settings.py` (test-only) | `TEST-012` | verified |
| `BUG-003` | `docs/spec/09-known-issues/BUG-003.md` | `docs/spec/03-feature-specs/2-1-gmail-oauth-authorization.md` | `AC-065` | `TASK-016` | `briefing/tests/services/test_gmail.py` (test-only) | `TEST-013` | verified |
| `BUG-004` | `docs/spec/09-known-issues/BUG-004.md` | `docs/spec/03-feature-specs/1-2-core-configuration-module.md` | `AC-066` | `TASK-017` | `briefing/tests/test_config.py` (test-only) | `TEST-002` | verified |
| `FR-028` | `docs/spec/05-change-requests/CR-003.md` | `docs/spec/03-feature-specs/5-5-music-classification.md`, `docs/spec/07-decisions/ADR-002.md` | `AC-067..AC-069` | `TASK-019`, `TASK-020`, `TASK-021`, `TASK-022` | `briefing/app/pipeline/stages/frame.py`, `briefing/pipeline_prompts/stages/frame.md` | `TEST-014` | verified |
| `FR-029` | `docs/spec/05-change-requests/CR-004.md` | `docs/spec/03-feature-specs/5-6-music-selection.md`, `docs/spec/07-decisions/ADR-003.md` | `AC-070..AC-073` | `TASK-023`, `TASK-024`, `TASK-025`, `TASK-026` | `briefing/app/services/music.py`, `briefing/app/pipeline/stages/draft.py` | `TEST-015` | verified |
| `BUG-005` | `docs/spec/09-known-issues/BUG-005.md` | `docs/spec/07-decisions/ADR-004.md` | `AC-074` | `TASK-029` | `briefing/app/pipeline/stages/tts_prep.py` | `TEST-016` | verified |
| `FR-030` | `docs/spec/05-change-requests/CR-005.md` | `docs/spec/03-feature-specs/6-4-audio-segment-plan.md`, `docs/spec/07-decisions/ADR-004.md` | `AC-074..AC-079` | `TASK-027..TASK-033` | `briefing/app/pipeline/handoff.py`, `briefing/app/pipeline/ordering.py`, `briefing/app/pipeline/stages/assemble.py`, `briefing/app/pipeline/stages/tts_prep.py`, `briefing/app/services/tts.py`, `briefing/app/pipeline/orchestrator.py`, `briefing/app/api/briefings.py` | `TEST-016` | verified |
| `FR-031` | `docs/spec/05-change-requests/CR-006.md` | `docs/spec/03-feature-specs/6-5-audio-mixing.md`, `docs/spec/07-decisions/ADR-005.md` | `AC-080..AC-085` | `TASK-034..TASK-040` | `briefing/app/services/mixing.py`, `briefing/app/services/tts.py`, `briefing/app/services/music.py`, `briefing/app/pipeline/stages/draft.py`, `briefing/app/pipeline/stages/tts_prep.py` | `TEST-017` | verified |
| `BUG-006` | `docs/spec/09-known-issues/BUG-006.md` | n/a — direct bug fix | `AC-086` | n/a | `briefing/app/main.py`, `briefing/app/templates/dashboard.html` | `TEST-018` | verified |
| `BUG-007` | `docs/spec/09-known-issues/BUG-007.md` | `docs/spec/03-feature-specs/6-5-audio-mixing.md` | `AC-087..AC-089` | n/a | `briefing/app/services/mixing.py` | `TEST-019` | verified |
| `FR-032` | `docs/spec/05-change-requests/CR-007.md` | `docs/spec/03-feature-specs/4-6-select-stage.md` | `AC-090` | `TASK-041`, `TASK-043` | `briefing/app/pipeline/stages/select.py` | `tests/pipeline/stages/test_select.py` | verified |
| `FR-013` (Check 1 revision) | `docs/spec/05-change-requests/CR-007.md` | `docs/spec/03-feature-specs/7-3-qa-gate-stage.md` | `AC-091` | `TASK-042`, `TASK-043` | `briefing/app/pipeline/stages/qa_gate.py` | `tests/pipeline/stages/test_qa_gate.py` | verified |
| `FR-033` | `docs/spec/05-change-requests/CR-008.md` | `docs/spec/03-feature-specs/13-1-youtube-transcript-ingest.md` | `AC-092..AC-093` | `TASK-044`, `TASK-047` | `briefing/app/services/youtube.py` | `tests/services/test_youtube.py` | verified |
| `FR-034` | `docs/spec/05-change-requests/CR-008.md` | `docs/spec/03-feature-specs/13-2-article-url-ingest.md` | `AC-094` | `TASK-045`, `TASK-047` | `briefing/app/services/article.py` | `tests/services/test_article.py` | verified |
| `FR-035` | `docs/spec/05-change-requests/CR-008.md` | `docs/spec/03-feature-specs/13-3-on-demand-ingest-ui-and-api.md` | `AC-095` | `TASK-046`, `TASK-047` | `briefing/app/api/briefings.py`, `briefing/app/pipeline/orchestrator.py` | `tests/services/test_youtube.py`, `test_article.py`, `tests/pipeline/test_ordering.py` | verified |
| `BUG-008` | `docs/spec/09-known-issues/BUG-008.md` | `docs/spec/05-change-requests/CR-009.md`, `docs/spec/03-feature-specs/13-2-article-url-ingest.md` | `AC-096..AC-097` | `TASK-048`, `TASK-049` | `briefing/app/services/article.py` | `tests/services/test_article.py` | verified |
| `BUG-009` | `docs/spec/09-known-issues/BUG-009.md` | `docs/spec/05-change-requests/CR-010.md`, `docs/spec/03-feature-specs/8-6-settings-depth-and-llm-provider.md` | `AC-098..AC-099` | `TASK-050`, `TASK-051`, `TASK-052` | `briefing/app/api/settings.py` | `tests/api/test_settings.py` | verified |
| `BUG-010` | `docs/spec/09-known-issues/BUG-010.md` | `docs/spec/05-change-requests/CR-011.md`, `docs/spec/03-feature-specs/2-1-gmail-oauth-authorization.md`, `2-2-label-based-email-fetch.md` | `AC-100..AC-102` | `TASK-053`, `TASK-054`, `TASK-055` | `briefing/app/services/gmail.py`, `briefing/app/api/settings.py` | `tests/services/test_gmail.py` | verified |
| `BUG-011` | `docs/spec/09-known-issues/BUG-011.md` | `docs/spec/05-change-requests/CR-012.md`, `docs/spec/03-feature-specs/9-3-missed-run-detection.md` | `AC-103..AC-104` | `TASK-056`, `TASK-057`, `TASK-058` | `briefing/app/api/briefings.py`, `briefing/app/main.py`, `briefing/app/templates/dashboard.html` | `tests/api/test_briefings.py`, `tests/api/test_dashboard.py` | verified |
| `BUG-012` | `docs/spec/09-known-issues/BUG-012.md` | `docs/spec/05-change-requests/CR-013.md` | n/a | `TASK-059` | `briefing/app/pipeline/orchestrator.py` | pre-existing `tests/pipeline/test_processed_log.py` | verified |
| `BUG-013` | `docs/spec/09-known-issues/BUG-013.md` | `docs/spec/05-change-requests/CR-013.md` | `AC-105..AC-106` | `TASK-060` | `briefing/app/services/music.py` | `tests/services/test_music.py` | verified |
| `BUG-014` | `docs/spec/09-known-issues/BUG-014.md` | `docs/spec/05-change-requests/CR-013.md` | `AC-107..AC-108` | `TASK-061` | `briefing/app/services/mixing.py` | `tests/services/test_mixing.py` | verified |
| `BUG-015` | `docs/spec/09-known-issues/BUG-015.md` | `docs/spec/05-change-requests/CR-013.md` | `AC-109` | `TASK-062` | `briefing/app/api/briefings.py` | `tests/api/test_briefings.py` | verified |
| `BUG-016` | `docs/spec/09-known-issues/BUG-016.md` | `docs/spec/05-change-requests/CR-013.md` | `AC-110..AC-111` | `TASK-063` | `briefing/app/services/llm.py` | `tests/services/test_llm.py` | verified |
| `BUG-017` | `docs/spec/09-known-issues/BUG-017.md` | `docs/spec/05-change-requests/CR-013.md` | `AC-112` | `TASK-064` | `briefing/app/api/briefings.py` | `tests/api/test_briefings.py` | verified |
| `BUG-018` | `docs/spec/09-known-issues/BUG-018.md` | `docs/spec/05-change-requests/CR-013.md` | `AC-113` | `TASK-065` | `briefing/app/api/briefings.py` | `tests/api/test_briefings.py` | verified |

## Coverage checklist

- [x] Every P0 requirement has acceptance criteria.
- [x] Every accepted requirement maps to at least one spec.
- [x] Every accepted requirement maps to implementation tasks.
- [x] Every accepted requirement maps to tests or an explicit manual verification method.
- [x] Every bug fix has a regression test or documented exception (as of the 2026-07-06 audit pass — `BUG-001` through `BUG-018` all have one).
- [x] Every ADR maps to affected requirements or constraints.
- [x] Deprecated and superseded requirements are not used for new work (`FR-006` marked superseded by `FR-032` via `CR-007`).

## Gaps

| Gap ID | Missing link | Impact | Owner | Due date |
|---|---|---|---|---|
| `GAP-001` (resolved 2026-07-06) | Epic 13 (FR-033/034/035) had no registry/traceability coverage despite shipped code | Medium — spec/code drift | Jason | Closed via `CR-008` |
| `GAP-002` | README/OAuth setup guide (spec 12-5) accuracy not yet re-verified against the current onboarding flow | Low — usability/docs only | Jason | Open — next audit pass |

