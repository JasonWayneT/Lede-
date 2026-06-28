# Story 5.3: Assemble Stage -- Briefing Document Assembly

Status: ready-for-dev

## Story

As a developer,
I want the assemble stage to organize all drafted stories into a single dated markdown briefing file grouped by section,
so that the output is a readable document the user can download and review.

## Acceptance Criteria

1. **Given** a HandoffPacket with `drafted_stories` and a section order from config, **When** the assemble stage runs, **Then** stories are organized into sections in the user-configured section order

2. **Given** stories within a section, **When** assembly orders them, **Then** stories are sorted by source count (most newsletters covering the story appears first)

3. **Given** the assembled briefing, **When** I read the markdown file, **Then** it contains a header with: date, run ID, total story count, and section breakdown (e.g. "AI: 3 stories, Technology: 2 stories")

4. **Given** the assembled markdown, **When** I inspect the file path, **Then** it is saved to `data/briefings/{run_id}/briefing.md`

5. **Given** the assemble stage, **When** it completes, **Then** `packet.assembled_markdown` contains the full markdown string and the `BriefingOutput` DB record is updated with `markdown_path`

6. **Given** the stage completing, **When** the orchestrator processes it, **Then** the HandoffPacket is written to `data/artifacts/{run_id}/stage_08_assemble.json`

## Tasks / Subtasks

- [ ] Implement `app/pipeline/stages/assemble.py` (AC: 1–6)
  - [ ] `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`
  - [ ] Group `packet.drafted_stories` by `section_name`
  - [ ] Order sections by `config.sections` order; "Other" always last
  - [ ] Within each section: sort by `source_count` descending
  - [ ] Build markdown string with header block and sections
  - [ ] Header format: `# Briefing — {date}\n\nRun #{run_id} | {total} stories | {section_breakdown}`
  - [ ] Each section: `## {section_name}\n\n{story_prose}\n\n---\n\n` per story
  - [ ] Save to `data/briefings/{run_id}/briefing.md` (create directory if needed)
  - [ ] Assign full markdown to `packet.assembled_markdown`
  - [ ] Write `BriefingOutput` DB record: `markdown_path = str(output_path)` — need DB session
  - [ ] Wrap exceptions in `StageError("assemble", str(e), retryable=False)`

- [ ] Write tests in `tests/pipeline/stages/test_assemble.py` (AC: 1–5)
  - [ ] Test section ordering matches `config.sections`
  - [ ] Test stories within section sorted by source_count desc
  - [ ] Test markdown header contains date, run_id, story count, section breakdown
  - [ ] Test file written to correct path
  - [ ] Test `assembled_markdown` field populated on packet

## Dev Notes

### DB write from stage (exception to the rule)

Architecture says "stages do NOT write to the DB — the orchestrator owns all DB writes." However, `BriefingOutput.markdown_path` must be written when the file is created, which happens in this stage. Options:
1. **Preferred:** Return the `markdown_path` in the packet and let the orchestrator write `BriefingOutput`
2. **Alternative:** Stage writes `BriefingOutput` with an injected session parameter

Use option 1: add `packet.markdown_path: str = ""` to HandoffPacket and let the orchestrator handle the DB write after assemble returns.

### Output file path

```
data/briefings/{run_id}/briefing.md
```

`{run_id}` is `packet.run_id`. Create the directory: `Path(config.data_dir) / "briefings" / str(packet.run_id)`.

### Section breakdown format

In header: `"AI: 3 stories | Technology: 2 stories | Other: 1 story"` — concatenate with ` | `.

### Date in header

Use `datetime.utcnow().strftime("%Y-%m-%d")` for the date in the header. This represents when the briefing was assembled.

### References

- [Source: docs/ARCHITECTURE.md § "Structure Patterns — Briefing Output Files"] — `data/briefings/{run_id}/briefing.md`
- [Source: docs/ARCHITECTURE.md § "Data Architecture — SQLite models"] — BriefingOutput schema
- [Source: docs/epics-stories.md § "Story 5.3"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
