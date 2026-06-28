# Story 12.3: Pipeline Stage Tests

Status: ready-for-dev

## Story

As a developer,
I want unit tests for each of the 9 pipeline stages using mock HandoffPackets and mocked external services,
so that stage logic is verified independently of Gmail, LLM providers, and TTS.

## Acceptance Criteria

1. **Given** the extract stage with a HandoffPacket containing raw HTML emails, **When** the test runs, **Then** `extracted_texts` is populated with clean text, title, sender, and date for each email

2. **Given** the cluster stage with pre-computed mock embeddings, **When** the test runs, **Then** texts with high cosine similarity are grouped into the same cluster

3. **Given** the select stage with a mock LLM returning section names, **When** the test runs, **Then** each cluster receives a section assignment; unmatched clusters go to "Other"

4. **Given** the draft stage with mock LLM responses for each depth tier, **When** the test runs, **Then** brief stories are 2-3 sentences, standard stories are paragraphs, deep stories are mini-segments

5. **Given** the qa_gate stage with a valid briefing package, **When** the test runs, **Then** `qa_passed = True` is set

6. **Given** the qa_gate stage with a briefing missing source attribution on a story, **When** the test runs, **Then** a `StageError` is raised with a message identifying the validation failure

7. **Given** every stage test, **When** it runs, **Then** no real LLM calls, Gmail calls, or TTS synthesis occur — all mocked via pytest fixtures

## Tasks / Subtasks

- [ ] Write `tests/pipeline/stages/test_extract.py` (AC: 1, 7)
  - [ ] Create test packet with HTML emails (inline fixtures, not real Gmail)
  - [ ] Test clean text output has no HTML tags
  - [ ] Test each output entry has: `email_id`, `text`, `title`, `sender_name`, `date`
  - [ ] Test malformed HTML email is skipped (WARNING logged, not StageError)

- [ ] Write `tests/pipeline/stages/test_embed.py` and `test_cluster.py` (AC: 2, 7)
  - [ ] Mock `embeddings.encode` returning controlled float vectors
  - [ ] Test embed stage: output vector count == input text count
  - [ ] Test cluster: pre-computed high-similarity vectors → same cluster
  - [ ] Test cluster: pre-computed low-similarity vectors → different clusters

- [ ] Write `tests/pipeline/stages/test_select.py` (AC: 3, 7)
  - [ ] Mock `llm.complete` returning section name string
  - [ ] Test all clusters receive section assignment
  - [ ] Test LLM returning unknown section → "Other" assigned

- [ ] Write `tests/pipeline/stages/test_frame.py` and `test_draft.py` (AC: 4, 7)
  - [ ] Mock `llm.complete` returning valid JSON (frame) and prose text (draft)
  - [ ] Test draft for brief/standard/deep — inspect mock call args to verify depth passed in prompt

- [ ] Write `tests/pipeline/stages/test_qa_gate.py` (AC: 5, 6, 7)
  - [ ] Test all checks pass → `qa_passed = True`
  - [ ] Test missing section → StageError
  - [ ] Test missing source attribution → StageError
  - [ ] Test TTS script with markdown → StageError
  - [ ] Confirm no LLM calls (no mock patch needed if no import exists)

- [ ] Write `tests/pipeline/stages/test_ingest.py`, `test_tts_prep.py`, `test_assemble.py` (AC: 7)
  - [ ] Ingest: mock `gmail.fetch_unprocessed_emails`, test early_halt on empty result
  - [ ] TTS prep: mock `llm.complete` returning JSON with script and pronunciation_guide
  - [ ] Assemble: test section ordering, story sort order, markdown file written to tmp_path

## Dev Notes

### Mock LLM in stage tests

Use `pytest.monkeypatch` or `unittest.mock.patch`:
```python
@pytest.mark.asyncio
async def test_select_assigns_sections(monkeypatch, mock_packet_for_select):
    async def mock_complete(prompt, config, **kwargs):
        return "AI"
    monkeypatch.setattr("app.services.llm.complete", mock_complete)
    result = await select.run(mock_packet_for_select, config)
    assert result.selected_clusters[0]["section_name"] == "AI"
```

### Stage interface validation

Every stage test must verify the function signature produces the correct output type:
```python
result = await stage.run(mock_packet, config)
assert isinstance(result, HandoffPacket)
```

### Controlled test vectors for cluster

Generate controlled similarity vectors in the test:
```python
import numpy as np
v1 = np.random.rand(384).astype(np.float32)
v2 = v1 + np.random.rand(384).astype(np.float32) * 0.01  # very similar
v3 = np.random.rand(384).astype(np.float32)               # unrelated
```

Normalize and use these as mock embeddings without actually loading sentence-transformers.

### References

- [Source: docs/ARCHITECTURE.md § "Testing Standards"] — mock HandoffPacket fixtures per stage
- [Source: docs/ARCHITECTURE.md § "Pipeline Stage Interface"] — `async def run(packet, config) -> HandoffPacket`
- [Source: docs/epics-stories.md § "Story 12.3"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
