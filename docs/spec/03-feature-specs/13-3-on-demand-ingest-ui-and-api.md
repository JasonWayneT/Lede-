# Story 13.3: On-Demand Ingest UI and API

Status: implemented (retroactive spec — see `CR-008`)

> **2026-07-06 note:** this spec was written after the code shipped, to close a documentation gap
> found during an audit pass (`AUDIT_LOG.md` finding P3). It describes actual current behavior in
> `app/api/briefings.py` (`start_on_demand`) and `app/pipeline/orchestrator.py`
> (`run_pipeline_on_demand`).

## Story

As a user,
I want to submit one or more YouTube or article URLs from the dashboard and get a briefing built
from just that content,
so that I can get a synthesized, listenable segment about specific content on demand, without
waiting for or mixing it into a scheduled newsletter run.

## Acceptance Criteria

1. **Given** `POST /api/briefings/on-demand` with a body of `{urls: [...], source_type: "youtube"|"article"}`, **When** `urls` is empty, **Then** it responds `422` ("At least one URL is required")

2. **Given** a `source_type` outside `"youtube"`/`"article"`, **When** the request is validated, **Then** it responds `422`

3. **Given** a Run already in `"running"` status, **When** an on-demand request arrives, **Then** it responds `409` ("A run is already in progress") — same single-active-run invariant as the scheduled/manual trigger

4. **Given** valid input, **When** the endpoint runs, **Then** it extracts content **synchronously** (via `fetch_transcripts`/`fetch_articles`, see `13-1`/`13-2`) *before* creating the `Run` row or starting the background pipeline

5. **Given** extraction yields zero usable `{url, text}` entries, **When** this is detected, **Then** the endpoint responds `422` ("No usable content could be extracted from the provided URLs") without ever creating a `Run` row

6. **Given** extraction yields at least one usable entry, **When** the endpoint proceeds, **Then** a `Run` row is created with `status="pending"` and `section_config` recording `sections`, `source_type`, and `source_urls`, and `orchestrator.run_pipeline_on_demand` is scheduled as a background task with the extracted texts

7. **Given** `run_pipeline_on_demand` executes, **When** it runs, **Then** it builds a fresh `HandoffPacket` with `extracted_texts` pre-populated and runs only `ON_DEMAND_STAGES` (`embed` through `qa_gate` — `ingest` and `extract` are skipped entirely, matching `STAGES[2:]`)

8. **Given** the on-demand pipeline completes, **When** it finalizes, **Then** it writes `BriefingOutput` and marks `Run.status = "complete"` exactly like a scheduled/manual run, and additionally records `story_count`, `section_breakdown`, and `source_type` onto `Run.section_config` for history/UI display

9. **Given** a stage failure during an on-demand run, **When** `StageError` is raised, **Then** it goes through the same `_retry`/Hold-state path as scheduled/manual runs (see `7-4-retry-and-hold-state.md`) — on-demand runs are not a separate failure-handling path

10. **Given** the same SSE `run_id`, **When** a browser is connected to `/api/stream/{run_id}`, **Then** on-demand runs stream `status`/`log`/`complete`/`error` events identically to scheduled/manual runs — no separate live-log wiring exists for this mode

## Implementation

- `app/api/briefings.py` — `OnDemandRequest` (Pydantic body), `POST /api/briefings/on-demand` (`start_on_demand`)
- `app/pipeline/orchestrator.py` — `ON_DEMAND_STAGES = STAGES[2:]`, `run_pipeline_on_demand(...)`
- Consumes `app/services/youtube.py` and `app/services/article.py` (see `13-1`, `13-2`)

## Known gaps (carried over from audit — not yet fixed by this CR)

- No cap on the number of URLs accepted per request, and extraction runs sequentially with per-URL timeouts — see `AUDIT_LOG.md` S3.
- The dashboard-side UI for submitting on-demand URLs was not independently re-verified in this documentation pass — recommend a follow-up spec/UI check.
