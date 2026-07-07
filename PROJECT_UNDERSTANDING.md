# Project Understanding — Lede

_Compiled from BMAD docs (product-brief, PRD, ARCHITECTURE, epics-stories), the docs/spec/ layer (constitution, requirements registry, traceability matrix, feature specs, ADRs, CRs, known issues), AGENTS.md, and a direct read of the implementation in `briefing/`. This is Phase 0 of a production-readiness audit — it establishes what the project claims to be before judging what it currently is._

## What BMAD says this project is for

Lede (originally named "Briefing") is a solo, local-first, self-hostable tool that pulls newsletters from a Gmail label, uses an LLM to cluster and synthesize cross-source stories into topic sections, and delivers the result as a markdown briefing plus an NPR-style audio file. Primary user: the author himself (dogfooding), secondary audience: other technical builders/PMs who might clone it. It is explicitly **not** a hosted, multi-user, or paid product in this version — it's a portfolio piece and a personal tool, MIT licensed, meant to demonstrate editorial-quality synthesis and clean self-hosted developer experience.

Success is defined narrowly: Jason uses it as his primary newsletter tool within 2 weeks, a new technical user can set it up in under 15 minutes, and duplicate stories collapse into one entry instead of piling up. There is an explicit counter-metric against feature creep: don't optimize for longer briefings or longer setup time.

## What the SDDs collectively claim

The project runs an unusually rigorous BMAD → `docs/spec/` methodology (see `AGENTS.md`, `PIPELINE.md`): every requirement gets an ID in `docs/spec/02-requirements-registry.md`, a feature spec under `docs/spec/03-feature-specs/`, and a row in `docs/spec/06-traceability/traceability-matrix.md`. As of this audit, the registry lists FR-001 through FR-031, ARCH-001 through ARCH-006, and BUG-001 through BUG-007, nearly all marked `verified`. 13 epics / 44+ stories are broken out in `docs/epics-stories.md`, covering: foundation/config/DB/credentials/errors (Epic 1), Gmail ingest (Epic 2), LLM provider routing (Epic 3), content pipeline (Epic 4), editorial synthesis (Epic 5), audio/TTS/music (Epic 6), orchestration/QA/retry (Epic 7), web UI (Epic 8), scheduling/daemon (Epic 9), onboarding (Epic 10), MCP server (Epic 11), testing (Epic 12), and on-demand YouTube/article ingest (Epic 13).

On paper, this is one of the best-documented solo projects of this size: nearly every requirement has an explicit acceptance criterion and a "verified" test status.

## Where implementation agrees with the docs

The large majority of what was checked matches. Confirmed solid:
- Core foundation (config, DB models, credential/keyring wrapper, error types) — exact match to spec, meaningful tests.
- Processed-log atomicity (the DB transaction that only records processed emails on full Run success) — verified directly in code, not just claimed.
- LLM provider routing (Ollama, OpenAI, Anthropic, Gemini, MCP sampling) — matches spec, no provider-specific code leaks into pipeline stages, no API keys logged anywhere.
- Extract/embed/cluster stages, HandoffPacket schema, condense/source-budget logic (the BUG-001 fix) — all match.
- Frame/draft/assemble stages, music classification & selection, audio segment planning, and the audio mixing DSP (ducking, looping, fades, transient compression) — all match their specs, and the mixing tests in particular do real signal-level assertions (fade ramps, loop-seam discontinuity, peak guards), not just smoke tests.
- Orchestrator retry tiers, Hold state, SSE live-log queue, BUG-002 (settings forms) and BUG-006 (dashboard hold-state visibility) fixes — all verified fixed.
- Scheduler, daemon mode, MCP server entry-point isolation — all match spec.

## Where implementation disagrees with the docs (drift — findings in their own right)

1. **Epic 13 (YouTube transcript ingest, article URL ingest, on-demand UI — PRD FR-26/27/28) has real, tested, wired-up code with zero coverage anywhere in the spec layer.** No feature spec file, no requirements-registry entry, no traceability row. This is a full feature (`services/youtube.py`, `services/article.py`, `pipeline/ordering.py`, `POST /api/briefings/on-demand`, a whole second orchestrator path `run_pipeline_on_demand`) that was built without following the project's own documented "specs before code" rule. It's also the area carrying the most novel risk (see Audit Log — SSRF).

2. **The `select` stage silently abandoned its core design.** The spec (4-6) and requirements registry (`FR-006`) both say each story cluster is classified into one of the user's *configured* topic Sections, falling back to "Other" only when nothing fits. The actual code no longer reads `config.sections` at all — it lets the LLM invent a freeform category name for every cluster. The test file for this stage even says so directly in a comment ("Sections are now derived freely from content rather than classified against a fixed taxonomy"), but no CR, ADR, or spec update documents this pivot — the traceability matrix still describes the old, no-longer-true behavior as `accepted`. This is either a deliberate, good design change that never got written down, or an accidental regression — it needs a decision, not just a doc fix (see Audit Log).

3. **`qa_gate`'s per-section coverage check was removed** without the spec (7-3, AC-1) being updated — code and tests agree with each other, but disagree with the written spec.

4. **The Gmail ingest stage has an undocumented "lookback window" feature** (reads `data/settings.json`, defaults to 7 days on any parse failure) with no requirement ID, spec, or traceability entry, despite being live behavior that changes which emails get fetched.

5. **The web UI has drifted from its documented shape**: `history.html` in the spec is `archive.html` in code; the dashboard's live log uses hand-rolled `EventSource` JS rather than the documented HTMX SSE extension; the entire onboarding wizard (`setup.py`, `/setup`, `/oauth/callback`) has no feature spec in the reviewed set.

6. **Missed-run detection (9-3) doesn't do what its own acceptance criterion requires.** The spec's AC-1 calls for a UI banner ("Missed run at 7:00 AM — retrying now"). The actual `GET /api/briefings/missed` endpoint is a hardcoded stub that always returns `missed_at: None`; the retry does fire, but silently in the background, with no way for the user to know it happened.

**Bottom line on Phase 0:** the documentation discipline is real and mostly honored, but there are several places — most notably the Section-classification pivot and the entire on-demand ingest feature — where code moved and the paper trail didn't follow. That's a genuine finding for a project whose entire methodology is built around "specs before code."
