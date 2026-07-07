# Definition of Done — Lede

_What "production-ready" means for this specific project, not a generic checklist. Read this before Phase 2 (deeper audit) or Phase 4 (fixes) proceeds — it determines what "finished" means, per the project's own documented intent._

## What kind of project this actually is

Lede is a **solo, self-hosted, local-first tool** — one user (Jason, dogfooding it daily), running on one machine, with a secondary goal of being a credible open-source project other technical builders might clone. It is explicitly **not**: a hosted service, a multi-user product, or something sold to paying customers in its current form. That means the bar below is calibrated to "a careful solo developer would trust this with their own Gmail account and run it unattended on a schedule," not "this survives a security audit for a SaaS handling other people's data at scale."

One reframe worth flagging up front: the source audit-loop instructions ask about "sellable" as its own category (paying-user data handling, support burden, licensing). Lede's own PRD explicitly puts a hosted/paid version out of scope for this version. I've translated "sellable" below into **"crediblely open-sourceable"** instead — is this something Jason could point people to on GitHub without embarrassment or real risk to a cloner. If the goal has shifted toward an actual paid/hosted product, the bar changes materially and this document should be redone.

## Checklist by category

### Correctness
- [x] Core pipeline (ingest → extract → embed → cluster → select → frame → draft → assemble → tts_prep → qa_gate) works end-to-end on realistic newsletter volume — confirmed via spec/code match across Epics 1–7.
- [x] **Decided:** the `select` stage's freeform-category behavior stays, as an intentional interim design (Jason: aggregate/average real category names later once there's enough data to derive a taxonomy). Documented via `CR-007`.
- [x] YouTube/article on-demand ingest (Epic 13) now has its spec/registry/traceability entries backfilled (`CR-008`) — verified against written acceptance criteria, not just "it has tests."
- [x] Settings — Sections/Depth/LLM Provider forms checked against `settings.html`: Depth and LLM Provider were broken (`BUG-009`, fixed); Sections has no form in the UI currently, consistent with the freeform-interim state above.

### Reliability
- [x] QA gate + 3-tier retry + Hold state work as designed for LLM-stage failures.
- [x] Audio failure degrades gracefully at the run level (missing Kokoro, corrupt asset) rather than failing the whole run.
- [x] Silent-failure paths closed: Gmail lookback-window parse (R1/`BUG-010`), raw `FileNotFoundError` in OAuth (R2/`BUG-010`), missing "missed run" UI banner (R3/`BUG-011`), malformed music-asset-JSON crash (R5/`BUG-013`), corrupt music file taking out a whole briefing's audio (R6/`BUG-014`).
- [ ] Daemon PID-reuse race (R8) — assessed, left open. Fixing it properly needs a new dependency (`psutil`) or a subprocess-based check on every dashboard load; flagged for Jason's call rather than decided silently, given the low probability of PID reuse in this window on a single-user machine.

### Security
- [x] **The SSRF risk in article ingest (S1)** — fixed (`BUG-008`/`CR-009`): scheme + resolved-IP guard rejecting loopback/private/link-local/reserved addresses, before any outbound fetch.
- [x] Credential handling (OAuth tokens, BYOK API keys) is solid — centralized through keyring, never logged, never in plaintext.
- [x] No XSS, no path traversal, no new CSRF surface found in the web UI.

### Performance
- [x] Realistic scale for this project (dozens of newsletters per run, one user, one machine) is well within what's been built — no evidence of anything falling over at the scale that matters here. Not re-litigating theoretical scale (thousands of users) since that's explicitly out of scope.

### Usability
- [ ] Not yet directly tested: whether a first-time technical user actually gets through `setup.py` → onboarding wizard → first briefing in under 15 minutes (PRD's own SM-2 success metric). This needs an actual walkthrough, not just a spec read.
- [ ] README/OAuth setup guide (spec 12-5) accuracy wasn't verified this pass.

### UI/UX
- [x] The dashboard/archive/settings pages exist and match most of their specs; small drifts (D1, D2) are documented as cosmetic/structural, not functional problems.
- [ ] Given this project is also meant to be a portfolio piece, a pass on visual polish and first-time-user flow (not just "does it technically render") is worth doing once functional gaps are closed — but this is explicitly lower priority than correctness/reliability/security above.

### Maintainability
- [x] The spec/traceability discipline itself is a real strength here — most requirements are genuinely traceable to code and tests.
- [x] The drift items (select.py, qa_gate.py, Epic 13, gmail lookback window) are reconciled — `docs/spec/` now describes actual current behavior for all of them.

### Packaging / operational readiness
- [x] MIT license, `uv` lockfile, `.env.example`, gitignored runtime data — all present and consistent with a clone-and-run open-source tool.
- [ ] Not yet verified: whether the README's OAuth setup steps still match the current `setup.py` flow (given the OAuth redirect-flow refactor referenced in BUG-003).

### "Crediblely open-sourceable" (the sellable-equivalent bar)
- Licensing: MIT, consistent, no flagged conflicts.
- Data handling: local-only, no telemetry observed, OAuth scope stays read-only — good story for anyone evaluating whether to trust this with their own Gmail.
- Support burden: as a portfolio piece with one real user, this isn't a live concern yet — worth revisiting only if Jason actually wants to invite outside contributors/users.
- **The SSRF gap (S1) — fixed.** This was the one item that actually mattered for this category; it's now closed.

## What "done" looks like for this pass

Not "zero findings" — that's not a realistic bar for a project this size, and chasing it would violate the project's own counter-metrics against scope creep. **This pass (Pass 2) met that bar**: the product-decision items (P1–P3) were resolved by Jason, every High-severity reliability/security item (S1, S2, R1–R3) is fixed with a regression test each, `docs/spec/` is back in sync with actual code behavior, and the full test suite (287 tests) is green. Remaining open items (R7's refactor, R8's dependency tradeoff, R11's low-value fix, the README/OAuth-guide check) are real but explicitly not blockers — see `AUDIT_LOG.md`'s "What's left" section for the plain-language breakdown.
