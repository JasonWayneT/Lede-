# Story 5.2: Draft Stage -- Story Synthesis

Status: ready-for-dev

## Story

As a developer,
I want the draft stage to generate one editorial story per cluster as broadcast-style prose at the assigned depth tier,
so that the briefing reads as if written by a single editor who synthesized multiple sources.

## Acceptance Criteria

1. **Given** a cluster with `depth_tier = "brief"`, **When** the draft stage synthesizes it, **Then** the resulting story is 2-3 sentences: headline plus essential context

2. **Given** a cluster with `depth_tier = "standard"`, **When** the draft stage synthesizes it, **Then** the resulting story is a short narrative paragraph covering what happened, why it matters, and local stakes

3. **Given** a cluster with `depth_tier = "deep"`, **When** the draft stage synthesizes it, **Then** the resulting story is a full mini-segment with nuance, conflicting angles if present, and background context

4. **Given** any drafted story, **When** I read it, **Then** it reads as natural spoken prose — no bullet points, no markdown headers within the story, no raw URLs

5. **Given** any drafted story, **When** I inspect it, **Then** source attribution is present — the names of newsletters that contributed are listed

6. **Given** any drafted story with guardrails from the frame stage, **When** I read it, **Then** hedging language is present for uncertain claims — no guardrail is silently dropped

7. **Given** the draft stage, **When** it synthesizes each story, **Then** it calls `llm.complete()` with a prompt from `pipeline_prompts/stages/draft.md`, passing only the cluster's framing fields — not the full pipeline history

8. **Given** the stage completing, **When** the orchestrator processes it, **Then** the HandoffPacket is written to `data/artifacts/{run_id}/stage_07_draft.json`

## Tasks / Subtasks

- [ ] Implement `app/pipeline/stages/draft.py` (AC: 1–8)
  - [ ] `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`
  - [ ] Load `pipeline_prompts/stages/draft.md`
  - [ ] For each framed story in `packet.framed_stories`:
    - [ ] Extract: `depth_tier`, `lead_angle`, `local_stakes`, `guardrails`, cluster texts, sender_names
    - [ ] Build prompt with these fields (not full HandoffPacket)
    - [ ] Call `await llm.complete(prompt, config)`
    - [ ] Build `drafted_story` dict: `{"section_name": ..., "depth_tier": ..., "prose": response, "sources": [sender_name, ...], "source_count": N}`
  - [ ] Assign list to `packet.drafted_stories`
  - [ ] Wrap LLM errors in `StageError("draft", str(e), retryable=True)`

- [ ] Create initial `pipeline_prompts/stages/draft.md` (AC: 4–7)
  - [ ] Prompt instructs: write broadcast prose, no markdown, no URLs, use specific depth tier instructions
  - [ ] Depth tier instructions embedded in prompt template
  - [ ] Include guardrails section: "The following hedging requirements must appear in your prose: {guardrails}"
  - [ ] Attribution instruction: end each story with "Sources: {source_names}"
  - [ ] Template variables: `{depth_tier}`, `{lead_angle}`, `{local_stakes}`, `{guardrails}`, `{cluster_texts}`, `{source_names}`

- [ ] Write tests in `tests/pipeline/stages/test_draft.py` (AC: 4–7)
  - [ ] Mock `llm.complete` returning prose text
  - [ ] Test `drafted_stories` list has one entry per framed story
  - [ ] Test `sources` field populated with sender names
  - [ ] Test prompt includes guardrails (inspect prompt passed to mock)

## Dev Notes

### Minimum context passed to LLM

AC 7 is explicit: the prompt passes only the cluster's framing fields, not the full HandoffPacket. Build the prompt from the framed story dict only. This keeps prompts focused and avoids token bloat.

### Style guide

The `pipeline_prompts/style-guide.md` file (created as a stub in Story 1.1) should be populated with broadcast prose style guidance and included in the draft prompt or as a persistent system prompt. Load it alongside `draft.md`.

### source attribution format

End each drafted story with: `"Sources: {comma-separated sender names}"`. The assemble stage (Story 5.3) may reformat this, but the draft stage must include it.

### References

- [Source: docs/ARCHITECTURE.md § "Pipeline Stage Interface"] — stage signature
- [Source: docs/ARCHITECTURE.md § "Structure Patterns — Handoff Artifact Files"] — `stage_07_draft.json`
- [Source: docs/epics-stories.md § "Story 5.2"] — acceptance criteria

## Amendment (CR-001 / FR-027 / ARCH-006)

The prompt-building snippet was a hard `entry.get("text", "")[:500]` slice per cluster source,
independent of (and inconsistent with) frame.py's 300-char slice — starving the writer of real
source content and producing generic, headline-level prose. Draft now reads
`story.get("source_texts")` (computed once by frame.py via `condense.get_source_texts()`) instead
of re-deriving text from the raw cluster; if `source_texts` is absent — e.g. an older persisted
handoff artifact replayed in a partial rerun — it falls back to computing condensed text per entry
itself. `draft.md` was also tightened to require claims grounded in source specifics rather than
generic "why it matters" commentary. See
`docs/spec/03-feature-specs/5-4-condense-long-sources.md` and `docs/spec/07-decisions/ADR-001.md`.
Original acceptance criteria (1-8 above) are unchanged and still hold.

## Amendment 2 (CR-004 / FR-029)

Each drafted story now also gets a `selected_music` field — `{"asset_id", "style", "file"}` or
`None` — computed via `app.services.music.select_music(segment_role="main_summary", ...)` from the
story's `section_name` and `sensitivity`. Not yet consumed by anything (audio mixing is Phase 5).
See `docs/spec/03-feature-specs/5-6-music-selection.md` and `docs/spec/07-decisions/ADR-003.md`.
Original acceptance criteria (1-8 above) are unchanged and still hold.

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
