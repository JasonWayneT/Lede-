# Story 4.1: HandoffPacket Schema and Disk I/O

Status: ready-for-dev

## Story

As a developer building pipeline stages,
I want a HandoffPacket dataclass with typed fields and helpers to read/write packets to disk,
so that all stages share a consistent data contract and partial reruns are possible without replaying previous stages.

## Acceptance Criteria

1. **Given** a pipeline stage completing its work, **When** it returns a HandoffPacket, **Then** the packet can be serialized to JSON and written to `data/artifacts/{run_id}/stage_{N:02d}_{stage_name}.json`

2. **Given** a serialized packet on disk, **When** the orchestrator reads it for a partial rerun, **Then** a HandoffPacket with all original fields is reconstructed without data loss

3. **Given** the HandoffPacket class, **When** I inspect it, **Then** it contains fields for: `run_id` (int), `emails` (list), `extracted_texts` (list), `embeddings` (list), `clusters` (list), `selected_clusters` (list), `framed_stories` (list), `drafted_stories` (list), `assembled_markdown` (str), `tts_script` (str), `pronunciation_guide` (dict), `qa_passed` (bool), `errors` (list)

3. **Given** `handoff-schema.yaml`, **When** I read it, **Then** every HandoffPacket field is documented with its type, which stage populates it, and which stages consume it

4. **Given** a stage that only needs `emails` and `extracted_texts`, **When** it receives the HandoffPacket, **Then** it reads only those fields — it does not inspect `embeddings`, `clusters`, or downstream fields

5. **Given** the `handoff.py` module, **When** imported by a stage, **Then** no imports from `api/`, `main.py`, or `mcp_server.py` appear

## Tasks / Subtasks

- [ ] Implement `HandoffPacket` dataclass in `app/pipeline/handoff.py` (AC: 1–3, 5)
  - [ ] Use Python `@dataclass` with `field(default_factory=...)` for mutable defaults
  - [ ] Fields: `run_id: int`, `emails: list = field(default_factory=list)`, `extracted_texts: list = field(default_factory=list)`, `embeddings: list = field(default_factory=list)`, `clusters: list = field(default_factory=list)`, `selected_clusters: list = field(default_factory=list)`, `framed_stories: list = field(default_factory=list)`, `drafted_stories: list = field(default_factory=list)`, `assembled_markdown: str = ""`, `tts_script: str = ""`, `pronunciation_guide: dict = field(default_factory=dict)`, `qa_passed: bool = False`, `errors: list = field(default_factory=list)`, `early_halt: bool = False`, `halt_reason: str = ""`
  - [ ] Add `early_halt` and `halt_reason` fields (not in epics but needed for ingest empty-list signaling to orchestrator)

- [ ] Implement disk I/O helpers in `app/pipeline/handoff.py` (AC: 1, 2)
  - [ ] `def write_packet(packet: HandoffPacket, artifacts_dir: Path, stage_num: int, stage_name: str) -> Path`: serialize to JSON, write to `{artifacts_dir}/{run_id}/stage_{stage_num:02d}_{stage_name}.json`, return path
  - [ ] `def read_packet(path: Path) -> HandoffPacket`: deserialize JSON back to HandoffPacket
  - [ ] JSON serialization: use `dataclasses.asdict()` — numpy arrays in `embeddings` must be converted to lists first
  - [ ] Create parent directory if it does not exist (`path.parent.mkdir(parents=True, exist_ok=True)`)

- [ ] Populate `pipeline_prompts/handoff-schema.yaml` (AC: 3)
  - [ ] Document each field: name, type, populated_by (stage name), consumed_by (list of stage names), description

- [ ] Write tests in `tests/pipeline/test_handoff.py` (AC: 1, 2, 5)
  - [ ] Test round-trip: create HandoffPacket → write to temp dir → read back → fields match
  - [ ] Test directory creation on write
  - [ ] Test file path pattern: `stage_03_embed.json`

## Dev Notes

### Embeddings serialization

`embeddings` will contain numpy float32 arrays from sentence-transformers. `dataclasses.asdict()` does not handle numpy arrays. Convert before serialization:

```python
import dataclasses, json, numpy as np

def _serialize(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Not serializable: {type(obj)}")

json.dumps(dataclasses.asdict(packet), default=_serialize)
```

On deserialization, lists are fine — numpy conversion happens in the embed stage, not in handoff.

### early_halt field

The ingest stage sets `packet.early_halt = True` and `packet.halt_reason = "no_new_emails"` when it finds no unprocessed emails. The orchestrator checks this flag after each stage and halts cleanly without raising a `StageError`.

### File path pattern (exact)

`data/artifacts/{run_id}/stage_{N:02d}_{stage_name}.json` — N is zero-padded to 2 digits:
- Stage 1 (ingest): `stage_01_ingest.json`
- Stage 3 (embed): `stage_03_embed.json`

### References

- [Source: docs/ARCHITECTURE.md § "Structure Patterns — Handoff Artifact Files"] — `data/artifacts/{run_id}/stage_{N:02d}_{stage_name}.json`
- [Source: docs/ARCHITECTURE.md § "Pipeline Stage Interface"] — `async def run(packet, config) -> HandoffPacket`
- [Source: docs/epics-stories.md § "Story 4.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
