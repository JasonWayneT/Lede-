# Story 4.6: Select Stage -- Section Classification

Status: ready-for-dev

## Story

As a developer,
I want the select stage to assign each cluster to a user-configured section using the LLM provider,
so that stories are organized by topic before synthesis.

## Acceptance Criteria

1. **Given** a HandoffPacket with `clusters` and `config` with `sections = ["AI", "Technology", "Finance"]`, **When** the select stage runs, **Then** it returns the packet with `selected_clusters` populated — each cluster has an assigned `section_name`

2. **Given** a cluster that does not match any configured section, **When** the select stage classifies it, **Then** it is assigned to the `"Other"` catch-all section — it is never dropped

3. **Given** each cluster, **When** classification runs, **Then** exactly one section is assigned — no cluster receives multiple sections

4. **Given** the select stage, **When** it makes its classification decision, **Then** it calls `llm.complete()` with a prompt loaded from `pipeline_prompts/stages/select.md` — the prompt is not hardcoded in the stage file

5. **Given** an LLM classification call that fails, **When** the stage encounters the error, **Then** it raises `StageError("select", message, retryable=True)`

6. **Given** the stage completing, **When** the orchestrator processes it, **Then** the HandoffPacket is written to `data/artifacts/{run_id}/stage_05_select.json`

## Tasks / Subtasks

- [ ] Implement `app/pipeline/stages/select.py` (AC: 1–6)
  - [ ] `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`
  - [ ] Load prompt template from `pipeline_prompts/stages/select.md` at stage start
  - [ ] For each cluster in `packet.clusters`: build prompt with cluster text summaries and available section names; call `await llm.complete(prompt, config)`; parse response to extract section name
  - [ ] If response does not match any configured section: assign `"Other"`
  - [ ] Ensure `"Other"` is always available as a fallback (add to sections list if not present)
  - [ ] Build `selected_cluster` dict: original cluster + `section_name` field
  - [ ] Assign list to `packet.selected_clusters`
  - [ ] Wrap LLM errors in `StageError("select", str(e), retryable=True)`

- [ ] Create initial `pipeline_prompts/stages/select.md` (AC: 4)
  - [ ] Prompt must: list available sections, include cluster text, ask for single section name only
  - [ ] Template variables: `{sections}` (comma-separated), `{cluster_texts}` (bullet list of text snippets)
  - [ ] Response format instruction: "Reply with exactly one section name from the list, nothing else."

- [ ] Write tests in `tests/pipeline/stages/test_select.py` (AC: 1–5)
  - [ ] Mock `llm.complete` returning a valid section name
  - [ ] Test fallback to "Other" when LLM returns unknown section name
  - [ ] Test each cluster gets exactly one section
  - [ ] Test `StageError` raised on LLM failure

## Dev Notes

### Prompt file loading

Load the prompt file once at stage entry, not at module import time:

```python
PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "pipeline_prompts" / "stages" / "select.md"

async def run(packet, config):
    prompt_template = PROMPT_PATH.read_text()
    for cluster in packet.clusters:
        prompt = prompt_template.format(sections=", ".join(config.sections), ...)
        response = await llm.complete(prompt, config)
```

### Response parsing

LLM may return the section name with extra whitespace or casing differences. Normalize: `response.strip()`, then case-insensitive match against `config.sections`. If no match → `"Other"`.

### Parallel vs sequential LLM calls

For the first implementation, call LLM sequentially per cluster. Do not parallelize — this is simpler and avoids rate limit issues. Parallelization can be added in a later optimization story.

### References

- [Source: docs/ARCHITECTURE.md § "Pipeline Stage Interface"] — stage signature
- [Source: docs/ARCHITECTURE.md § "Data Boundaries — Prompts"] — stages read from `pipeline_prompts/stages/`
- [Source: docs/epics-stories.md § "Story 4.6"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
