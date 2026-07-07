# Audit Log — Lede

Living document. Every pass appends findings and updates status. See `PROJECT_UNDERSTANDING.md` for how these were discovered and `DEFINITION_OF_DONE.md` for the bar these are judged against.

**Pass 1 — 2026-07-06.** Scope: cross-referenced all `docs/spec/03-feature-specs/` files (Epics 1–13) against actual code in `briefing/`. Reading and comparison only — nothing fixed yet.

**Pass 2 — 2026-07-06.** Scope: resolved all three product-decision items per Jason's direction, then implemented every fixable finding at Medium+ severity using this project's own documentation-first workflow (CR + registry + traceability, fix, regression test, full-suite verification). Full suite (`uv run pytest`) is green: **287 passed**, 0 failures, after all changes below. Two items were assessed and deliberately left unfixed with the reasoning recorded — see their rows.

---

## Findings

### Product-decision items (owner decided — see resolution)

| # | Category | Severity | Finding | Status |
|---|---|---|---|---|
| P1 | Correctness / Product | **High** | The `select` pipeline stage (`briefing/app/pipeline/stages/select.py`) no longer classifies stories into the user's configured topic Sections. It lets the LLM invent a freeform category name per story instead. | **Resolved — kept as intentional interim behavior.** Jason: content is too varied right now to pick a fixed topic list; plan is to aggregate/average the freeform names that appear over enough runs and derive a real taxonomy later. Documented via `CR-007`: `FR-006` marked superseded by new `FR-032`, spec `4-6-select-stage.md` rewritten to describe current behavior, traceability updated. No code changed. |
| P2 | Product / Docs | Medium | `qa_gate.py` no longer checks that every configured Section has at least one story (spec 7-3 AC-1) — it only checks that *some* stories exist anywhere. | **Resolved — documentation fixed.** Same root cause as P1 (freeform sections make per-section coverage meaningless). `CR-007` rewrote spec `7-3-qa-gate-stage.md` AC-1 to match current code; registry `FR-013` updated with a note. No code changed. |
| P3 | Docs / Process | Medium | Epic 13 (YouTube ingest, article ingest, on-demand UI — PRD FR-26/27/28) is fully built and tested but has no feature spec, no registry entry, no traceability row. | **Resolved — documentation backfilled.** `CR-008` added `13-1-youtube-transcript-ingest.md`, `13-2-article-url-ingest.md`, `13-3-on-demand-ingest-ui-and-api.md`, plus registry entries `FR-033`/`FR-034`/`FR-035` and traceability rows. No code changed by this CR itself (see S1 below for a real bug found in this area). |

### Security

| # | Category | Severity | Finding | Status |
|---|---|---|---|---|
| S1 | Security | **High** | `briefing/app/services/article.py` fetches arbitrary user-supplied URLs server-side with no scheme/host allowlist and no private-IP/localhost blocking — a classic SSRF pattern via `POST /api/briefings/on-demand`. | **Fixed (`BUG-008`/`CR-009`).** Added `_is_url_safe_to_fetch()`: rejects non-http(s) schemes and hosts resolving to loopback/private/link-local/multicast/reserved addresses; fails open on unresolvable/slow DNS (ordinary fetch failure, not a security concern). 9 regression tests in `tests/services/test_article.py`. |
| S2 | Security / Reliability | High (confirmed) | Settings — Sections, Depth, and LLM Provider PUT routes took **JSON** bodies while `settings.html` submits Depth and LLM Provider as plain HTML forms — a `BUG-002`-class recurrence. Confirmed: Depth and LLM Provider forms exist and are broken; Sections has no form in the UI at all (consistent with P1's interim state), so its JSON body isn't mismatched with anything. | **Fixed (`BUG-009`/`CR-010`).** Converted `update_depth`/`update_llm` to `Form(...)` matching `settings.html`'s actual field names. Existing tests updated to submit form-encoded data; added explicit JSON-body-now-rejected regression tests. |
| S3 | Reliability | Medium | On-demand ingest has no cap on the number of URLs submitted; a long list is processed sequentially with per-URL timeouts. | **Fixed (`BUG-017`/`CR-013`).** Capped at 10 URLs per request (`422` above that, before any extraction work begins). |

### Reliability

| # | Category | Severity | Finding | Status |
|---|---|---|---|---|
| R1 | Reliability | **High** | `_lookback_query` silently swallowed all errors parsing `data/settings.json`, falling back to 7 days with no log line. | **Fixed (`BUG-010`/`CR-011`).** Logs a `WARNING` (path + exception) before falling back; the `int()` parse of `lookback_days` is now covered by the same try/except. |
| R2 | Reliability | High | `get_credentials_path` raised a raw `FileNotFoundError` instead of `StageError`, reachable mid-OAuth flow. | **Fixed (`BUG-010`/`CR-011`).** `build_auth_url`/`exchange_code` now re-raise as `StageError(retryable=False, code=AUTH_ERROR)`; the two `api/settings.py` callers updated to catch `StageError`. |
| R3 | Reliability | High | Missed-run retry (`GET /api/briefings/missed`) is a hardcoded stub always returning `missed_at: None` — no user-visible signal despite the retry firing correctly in the background. | **Fixed (`BUG-011`/`CR-012`).** Endpoint now derives real state from `check_missed_runs` + an active-run check; dashboard renders a "Missed run at {time} — retrying now" banner. |
| R4 | Reliability | Medium | A duplicate `email_id` at Run finalization would violate the unique constraint and roll back the whole commit. | **Fixed (`BUG-012`/`CR-013`).** Already-processed IDs are queried and skipped before insert, with a warning logged if any were found. |
| R5 | Reliability | Medium | `load_music_assets` raised uncaught on malformed `music_assets.json`, crashing `draft`/`tts_prep` entirely. | **Fixed (`BUG-013`/`CR-013`).** Catches parse/OS errors, degrades to no-music (same as the missing-file case). |
| R6 | Reliability | Medium | A corrupt/zero-length music file in `_load_music` took out audio for the *entire* briefing, not just the one segment. | **Fixed (`BUG-014`/`CR-013`).** Catches the read error, degrades to no-music for that one segment. |
| R7 | Reliability | Medium | Retry/resume logic is duplicated between `orchestrator.py`'s main loop and `briefings.py`'s `_resume` function. | **Assessed, not refactored — flagged.** A shared-helper refactor touches the core retry/completion path and is higher-risk than the other fixes in this pass. While assessing it, found and fixed a real bug this duplication had caused — see `BUG-018` below. Refactor itself remains open; see `CR-013`. |
| R8 | Reliability | Medium | `check_daemon_alive` checks liveness via `os.kill(pid, 0)` with no process-identity check — a PID-reuse race could misidentify an unrelated process as the daemon. | **Assessed, not fixed — flagged for owner.** Closing this properly needs either a new dependency (`psutil`) or a subprocess-based check (`ps`/`tasklist`) on every dashboard load. Per this project's own rule (flag new dependencies, don't add silently) and the low probability of PID reuse in this window on a single-user machine, left open pending Jason's call — see `CR-013`. |
| R9 | Reliability | Low-Medium | Check-then-act races on "is a Run already active" for both manual and on-demand triggers; check also missed the "pending" window. | **Fixed (`BUG-015`/`CR-013`).** Check moved into the same transaction as the insert (SQLite serializes concurrent writers); check broadened to `["running", "pending"]`. |
| R10 | Reliability | Medium | Gemini auth errors classified by lowercased substring matching instead of typed exceptions. | **Fixed (`BUG-016`/`CR-013`).** Uses `google.api_core.exceptions.Unauthenticated`/`PermissionDenied`, matching the OpenAI/Anthropic pattern. |
| R11 | Reliability | Low | `condense.py` discards all prior chunk output on a mid-batch chunk failure, forcing a full redo on retry. | **Assessed, accepted as-is.** Spec-compliant (retryable); the cost is a slower retry, not incorrect behavior. Not fixed — proportionality call, not worth the complexity of partial-result caching for a low-frequency retry path. |
| R12 | Reliability | Low | `_render_samples_sync`'s zero-audio `RuntimeError` path wasn't tested against whitespace-only input. | **Test coverage added.** Behavior was already correct (degrades to a non-fatal `StageError`); added `test_render_samples_raises_runtime_error_on_empty_pipeline_output` and `test_synthesize_whitespace_only_script_is_non_fatal_stage_error` to `tests/services/test_tts.py`. No code change needed. |

### Bug found during this pass, beyond the original findings

| # | Category | Severity | Finding | Status |
|---|---|---|---|---|
| — | Correctness | Medium | While assessing R7, found that `briefings.retry_run`'s `_resume` never recorded `ProcessedEmail` rows on successful completion — a retried run would let the next run re-fetch and reprocess the same emails, breaking FR-003's dedup guarantee. | **Fixed (`BUG-018`/`CR-013`).** Added the same insert (with the R4/`BUG-012` dedup guard) to `_resume`'s finalize block. |

### Documentation / drift (non-security, non-reliability)

| # | Category | Severity | Finding | Status |
|---|---|---|---|---|
| D1 | Docs | Low | Spec references `history.html`; actual template is `archive.html`, with `/history` redirecting to `/archive`. | **Fixed.** Noted in `8-3-briefing-history-and-downloads.md` — cosmetic rename, behavior unaffected. |
| D2 | Docs | Low | Dashboard's live-log wiring uses hand-rolled `EventSource` JS, not the documented HTMX SSE extension. | **Fixed.** Noted in `8-2-dashboard-run-trigger-and-live-log.md` — functionally equivalent, different transport than originally documented. |
| D3 | Docs | Low | The onboarding wizard was flagged as having no feature spec. | **False alarm, corrected.** `10-1-first-run-onboarding-wizard.md` and `10-2-onboarding-status-and-revisit.md` already exist and match code — the original finding came from an audit agent whose assigned slice didn't include Epic 10's specs. No action needed. |
| D4 | Docs | Low | TTS Engine Settings (spec 6-3) was not verified against code in this pass. | **Verified, matches.** `6-3-tts-engine-settings.md` status updated to `implemented`; confirmed against `api/settings.py`'s `/tts` routes, including the pre-existing `BUG-002` fix. |

### Things checked and found clean (for the record, so they aren't re-audited from scratch)

- No secrets (OAuth tokens, API keys) logged or written in plaintext anywhere — credential access is centralized through `credentials.py`/keyring as designed.
- No XSS in Jinja2 templates — default autoescaping is in effect everywhere checked, no `|safe` filters on user-influenced content.
- No path traversal in download endpoints — file paths are server-generated from the DB, never client-supplied.
- No new CSRF exposure — all routes remain same-origin, cookie-free, localhost-bound.
- Empty/huge input handling in the embed/cluster/condense stages degrades safely rather than crashing.
- Audio mixing DSP has genuine signal-level test coverage (fade ramps, loop-seam continuity, peak guards), not just smoke tests.

---

## Coverage note (Pass 2)

Every Medium+ finding from Pass 1 is now either fixed-with-a-regression-test, or explicitly assessed
and left open with reasoning recorded (R7's refactor, R8's dependency tradeoff, R11's low-value
cost/benefit). Full suite: `uv run pytest` → **287 passed, 0 failed**. Not yet done: README/OAuth
setup guide accuracy (spec 12-5) — the one item from Pass 1's coverage note still outstanding.

## What's left (plain language)

**Technical work remaining (small):**
- Verify the README's Google Cloud OAuth setup steps still match the current onboarding flow (spec 12-5) — not yet checked.
- Two accepted trade-offs, not blockers: the daemon liveness check has a very-low-probability PID-reuse edge case (R8 — would need a new dependency to fully close), and the retry-path code duplication (R7) is a maintainability wart, not a live bug (the one real bug it was hiding, `BUG-018`, is fixed).

**Business decisions, not technical work:**
- None outstanding this pass — the three product-decision items (P1–P3) were resolved by Jason at the start of this pass.

**Two consecutive passes without new Medium+ findings?** No — this is only Pass 2, and Pass 2 fixed everything Pass 1 found. A Pass 3 covering fresh ground (the README/OAuth check above, plus anything Pass 1's agents didn't reach) is the natural next step before calling the technical side "converged."
