# Story 8.5: Settings -- Topic Sections Management

Status: ready-for-dev

## Story

As a user,
I want to add, rename, remove, and reorder my topic sections from Settings,
so that my briefing is organized around the topics I actually care about.

## Acceptance Criteria

1. **Given** the Settings -- Sections page, **When** I view it, **Then** all currently configured sections are listed with their names and order

2. **Given** I click "Add Section" and type a name then save, **When** I save, **Then** the new section appears in the list and is used on the next Run

3. **Given** I try to delete the last remaining section, **When** I click delete, **Then** the UI prevents deletion with the message: "At least one section is required"

4. **Given** the "Other" catch-all section, **When** I view the section list, **Then** it appears in the list but cannot be renamed or deleted

5. **Given** I reorder sections and save, **When** the save completes, **Then** the new order is persisted and applied to the next Run

## Tasks / Subtasks

- [ ] Implement sections settings endpoints in `app/api/settings.py` (AC: 1–5)
  - [ ] `GET /api/settings/sections` → `{"data": {"sections": ["AI", "Technology", "Finance", "Other"]}}`
  - [ ] `PUT /api/settings/sections` → accepts `{"sections": [...]}` (ordered list, "Other" always appended if missing)
  - [ ] Validate: list must have at least 1 non-"Other" section; if empty, return 400 with "At least one section is required"
  - [ ] Validate: "Other" cannot be removed or renamed — enforce in PUT handler
  - [ ] Persist to `data/settings.json` and update in-memory config

- [ ] Add Settings -- Sections UI to `app/templates/settings.html` (AC: 1–5)
  - [ ] List of sections with drag-to-reorder (use HTML5 drag-and-drop, no JS framework)
  - [ ] Each section row: section name, delete button (disabled for "Other" and for last remaining non-Other)
  - [ ] "Add Section" inline form: text input + "Add" button
  - [ ] Save order button: HTMX PUT with ordered section list
  - [ ] "Other" row: no delete button, label shows "(catch-all, cannot be removed)"

- [ ] Write tests in `tests/api/test_settings.py` (AC: 2–5)
  - [ ] Test PUT with empty list → 400
  - [ ] Test PUT with only "Other" → 400
  - [ ] Test PUT without "Other" → "Other" auto-appended
  - [ ] Test section order persisted

## Dev Notes

### "Other" invariant

"Other" is always the last section. It cannot be removed, renamed, or reordered above other sections. The API enforces this:
1. If "Other" is in the submitted list at a non-last position, move it to the end.
2. If "Other" is not in the submitted list, append it.
3. If the submitted list consists only of "Other", return 400.

### Drag-to-reorder UI

Use HTML5 drag-and-drop with `draggable="true"` attributes and JavaScript event listeners. This is minimal JS — HTMX does not handle drag-and-drop natively. On drop, update a hidden input with the new order, then submit via HTMX PUT.

Alternatively: use up/down arrow buttons for reordering — simpler and no JS required beyond HTMX.

### Section names in AppConfig

`config.sections` is the in-memory list. After a PUT, update this list in memory AND write to `data/settings.json` for persistence across restarts.

### References

- [Source: docs/epics-stories.md § "Story 8.5"] — acceptance criteria
- [Source: docs/ARCHITECTURE.md § "Format Patterns — API Error Envelope"] — 400 validation errors

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
