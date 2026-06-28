# Story 5.1: Frame Stage -- Depth Tier Assignment

Status: ready-for-dev

## Story

As a developer,
I want the frame stage to assign each cluster a depth tier, lead angle, and guardrails before synthesis,
so that story drafts vary in length and focus based on the global depth setting and source strength.

## Acceptance Criteria

1. **Given** a HandoffPacket with `selected_clusters` and `config.briefing_depth = "standard"`, **When** the frame stage runs, **Then** each cluster in the result has: `depth_tier` (str: `"brief"|"standard"|"deep"`), `lead_angle` (str), `local_stakes` (str), `guardrails` (list[str])

2. **Given** `config.briefing_depth = "brief"`, **When** the frame stage runs, **Then** all clusters receive `depth_tier = "brief"` as the baseline; source-strength may upgrade clusters with many sources

3. **Given** a cluster with uncertain or unverified claims, **When** the frame stage analyzes it, **Then** the `guardrails` field contains explicit hedging instructions carried into the draft stage

4. **Given** the frame stage, **When** it makes its framing decisions, **Then** it calls `llm.complete()` with a prompt from `pipeline_prompts/stages/frame.md`

5. **Given** the stage completing, **When** the orchestrator processes it, **Then** the HandoffPacket is written to `data/artifacts/{run_id}/stage_06_frame.json`

## Tasks / Subtasks

- [ ] Implement `app/pipeline/stages/frame.py` (AC: 1–5)
  - [ ] `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`
  - [ ] Load prompt template from `pipeline_prompts/stages/frame.md`
  - [ ] For each cluster in `packet.selected_clusters`:
    - [ ] Determine source_count: `len(cluster["texts"])` (number of newsletters covering it)
    - [ ] Calculate baseline depth: `config.briefing_depth`
    - [ ] Upgrade logic: if `source_count >= 3` and baseline is `"brief"` → upgrade to `"standard"`; if `source_count >= 5` and baseline is `"standard"` → upgrade to `"deep"`
    - [ ] Build prompt with cluster texts, section, baseline depth, source count
    - [ ] Call `await llm.complete(prompt, config)` — LLM returns `lead_angle`, `local_stakes`, `guardrails`
    - [ ] Parse JSON response or structured response into fields
    - [ ] Enrich cluster dict with `depth_tier`, `lead_angle`, `local_stakes`, `guardrails`
  - [ ] Assign enriched list to `packet.framed_stories`
  - [ ] Wrap LLM errors in `StageError("frame", str(e), retryable=True)`

- [ ] Create initial `pipeline_prompts/stages/frame.md` (AC: 4)
  - [ ] Prompt instructs LLM to return a JSON object with exactly: `{"lead_angle": "...", "local_stakes": "...", "guardrails": ["...", ...]}`
  - [ ] Template variables: `{section}`, `{cluster_texts}`, `{depth_tier}`, `{source_count}`

- [ ] Write tests in `tests/pipeline/stages/test_frame.py` (AC: 1–4)
  - [ ] Mock `llm.complete` returning valid JSON
  - [ ] Test depth upgrade logic: 5 sources + standard config → deep tier
  - [ ] Test guardrails propagated from LLM response

## Dev Notes

### LLM response format

Ask the LLM to return JSON in the prompt. Parse with `json.loads(response.strip())`. If parsing fails, log WARNING and use safe defaults: `lead_angle="", local_stakes="", guardrails=[]`.

### Depth upgrade thresholds

These are implementation decisions not specified in the epics — use the thresholds above (3 sources for brief→standard, 5 sources for standard→deep). These can be made configurable in a later story.

### guardrails field purpose

`guardrails` is a list of plain-English instructions for the draft stage, e.g. `["Cite sources for the revenue figure", "Note that this is preliminary reporting"]`. The draft stage must not drop or ignore these — they flow directly into the drafting prompt.

### framed_stories vs selected_clusters

`packet.framed_stories` is a new field (list of enriched cluster dicts) populated by this stage. `packet.selected_clusters` is read but not modified. The enriched clusters are downstream from selected_clusters.

### References

- [Source: docs/ARCHITECTURE.md § "Pipeline Stage Interface"] — stage signature
- [Source: docs/ARCHITECTURE.md § "Structure Patterns — Handoff Artifact Files"] — `stage_06_frame.json`
- [Source: docs/epics-stories.md § "Story 5.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
