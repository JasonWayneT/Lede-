# Story 5.4: Conditional Source Condensation

Status: done

## Story

As a listener of the audio briefing,
I want stories to explain what actually happened, not just restate a headline,
so that the briefing is worth listening to instead of a teaser for emails I'd have to go read anyway.

Traces to `FR-027`, `ARCH-006`, `BUG-001`. Design rationale in `docs/spec/07-decisions/ADR-001.md`.

## Acceptance Criteria

1. **Given** a source entry whose cleaned text length is <= `SOURCE_TEXT_BUDGET_CHARS` (4000),
   **When** `condense.get_source_texts()` processes it, **Then** the text is returned unchanged and
   no LLM call is made (`AC-058`)

2. **Given** a source entry whose cleaned text length is > `SOURCE_TEXT_BUDGET_CHARS`,
   **When** condensation runs, **Then** the text is split into chunks on sentence boundaries only —
   no chunk ends mid-sentence — each chunk sent through the extraction-only prompt in
   `pipeline_prompts/stages/condense.md`, and the per-chunk outputs concatenated (`AC-059`)

3. **Given** a cluster of source entries, **When** the frame stage runs, **Then** it computes
   `source_texts` (one entry per cluster source, condensed-or-original) once and stores it on the
   framed story dict (`AC-057`, `AC-060`)

4. **Given** a framed story with `source_texts` present, **When** the draft stage runs,
   **Then** it builds its prompt from `story["source_texts"]` directly — it does not re-derive or
   re-truncate from the raw cluster (`AC-060`)

5. **Given** a framed story where `source_texts` is absent (e.g. an older persisted handoff artifact
   from before this story, replayed in a partial rerun), **When** the draft stage runs,
   **Then** it falls back to computing condensed text per cluster entry itself, so behavior degrades
   gracefully rather than raising

6. **Given** any Ollama-routed LLM call (frame's own prompt, draft's own prompt, or a condensation
   chunk), **When** the request is built, **Then** `options.num_ctx` is set from
   `config.ollama_num_ctx` (`AC-056`) — this is what makes passing full/condensed source text safe
   instead of silently truncated a second time by Ollama's own 2048-token default

## Tasks / Subtasks

- [x] Add `AppConfig.ollama_num_ctx: int = 8192` (`TASK-009`)
- [x] Set `options.num_ctx` in `_ollama_complete` request body (`TASK-009`)
- [x] Implement `app/services/condense.py`: `SOURCE_TEXT_BUDGET_CHARS`, `CONDENSE_CHUNK_CHARS`,
      sentence-boundary chunker, `condense()`, `get_source_texts(cluster, config)` (`TASK-010`)
- [x] Create `pipeline_prompts/stages/condense.md` extraction-only prompt (`TASK-010`)
- [x] Wire `frame.py` to call `condense.get_source_texts()` and store `source_texts` on each framed
      story (`TASK-011`)
- [x] Update `draft.py` to read `story.get("source_texts")` with a per-entry fallback (`TASK-012`)
- [x] Tighten `pipeline_prompts/stages/draft.md` to require claims grounded in source specifics
      (`TASK-013`)
- [x] Tests: `tests/services/test_llm.py` num_ctx assertion, new `tests/services/test_condense.py`,
      `source_texts` coverage in `tests/pipeline/stages/test_frame.py` and `test_draft.py`
      (`TASK-014`)

## Dev Notes

### Why sentence boundaries, not paragraph boundaries

`extract.py`'s `_WHITESPACE = re.compile(r"\s{2,}")` collapses most paragraph-separating newline
runs to a single space during HTML-to-text extraction, so `entry["text"]` does not reliably
preserve paragraph structure. Chunking on sentence boundaries (`(?<=[.!?])\s+`) is robust
regardless of whether paragraph structure survived extraction — see `ADR-001`.

### Why no separate reduce LLM call

Frame and draft already synthesize across a cluster's sources (that's their existing job). Adding
a dedicated reduce pass on top of the condensation map step would be a second summarization hop for
no benefit — it's cheaper and less hallucination-prone to let the map step's concatenated facts
feed directly into the stage that already does synthesis.

### Budget constants are fixed, not derived from num_ctx

`SOURCE_TEXT_BUDGET_CHARS` (4000) and `CONDENSE_CHUNK_CHARS` (3000) are module constants in
`condense.py`, chosen to be safe under the new `ollama_num_ctx` default (8192) with room for
multiple sources per cluster plus prompt scaffolding and generation. They are not derived
dynamically per-provider or per-`num_ctx` value — see `ADR-001` negative consequences.

### References

- `docs/spec/07-decisions/ADR-001.md` — full rationale and alternatives considered
- `docs/spec/09-known-issues/BUG-001.md` — the `num_ctx` bug this story's fix depends on
- [Source: conversation 2026-07-04] — PM-reported symptom ("audio brief is too short... talks
  about headlines but the user should actually learn what the stories are about")

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

### Completion Notes List

- Implemented as part of `CR-001`.

### File List

- `briefing/app/core/config.py`
- `briefing/app/services/llm.py`
- `briefing/app/services/condense.py` (new)
- `briefing/pipeline_prompts/stages/condense.md` (new)
- `briefing/app/pipeline/stages/frame.py`
- `briefing/app/pipeline/stages/draft.py`
- `briefing/pipeline_prompts/stages/draft.md`
- `briefing/.env.example`
- `briefing/tests/services/test_llm.py`
- `briefing/tests/services/test_condense.py` (new)
- `briefing/tests/pipeline/stages/test_frame.py`
- `briefing/tests/pipeline/stages/test_draft.py`
