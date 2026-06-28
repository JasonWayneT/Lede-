# BMAD Intake

Paste or summarize BMAD outputs here. This is the staging area before requirements are normalized into project specs.

## Source artifacts

| Source ID | BMAD artifact | Owner/agent | Date | Link or location | Status |
|---|---|---|---|---|---|
| `BMAD-SRC-001` | Product brief | PM | 2026-06-26 | `docs/product-brief.md` | imported |
| `BMAD-SRC-002` | PRD | PM | 2026-06-26 | `docs/PRD.md` | imported |
| `BMAD-SRC-003` | Architecture | PM/Agent | 2026-06-26 | `docs/ARCHITECTURE.md` | imported |
| `BMAD-SRC-004` | Epics & stories | PM/Agent | 2026-06-26 | `docs/epics-stories.md` | imported |

## Artifact mapping

| BMAD output | Destination spec |
|---|---|
| Brief, brainstorm, market research, domain research | `00-project-constitution.md`, PRD notes, context sections |
| PRD | `02-requirements-registry.md`, feature specs |
| Epics and stories | Feature specs, tasks, acceptance criteria |
| Architecture | Design specs, architecture requirements, ADRs |
| UX design | UX and design requirements, design specs |
| Dev stories | Tasks, acceptance criteria, test specs |
| QA test generation | Test specs and traceability matrix |
| Correct course output | Change requests and updated requirements |

## Raw BMAD notes

Paste raw or lightly edited BMAD content below.

```text
See the source artifacts above. This file summarizes import decisions and conflicts.
```

## Normalization notes

- Which requirements were imported?
  - Imported the canonical requirement set from `docs/PRD.md` (§4 Features + NFRs) and the story breakdown from `docs/epics-stories.md`.
  - Imported architecture constraints/patterns from `docs/ARCHITECTURE.md` (naming, boundaries, stack, file tree, provider routing, SSE shape).
- Which assumptions were converted to explicit requirements?
  - None yet at the registry layer; assumptions remain documented in `docs/PRD.md` (§9 Assumptions Index) and will be promoted to explicit requirements only when they affect implementation choices.
- Which conflicts were found?
  - `docs/product-brief.md` lists Web UI + scheduling + native TTS as V1 out-of-scope, but `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/epics-stories.md` include Web UI, scheduling/daemon mode, and Kokoro TTS in MVP scope. Per `AGENTS.md`, the working spec layer follows `docs/spec/` normalization from PRD + Architecture + Epics. The implementation will proceed per the story specs.
- Which open questions remain?
  - Provider/model defaults (e.g., default Ollama model name) remain open but are not required for Story 1.1 scaffolding.

## Import log

| Date | Imported by | Source IDs | Result | Follow-up |
|---|---|---|---|---|
| 2026-06-26 | Cursor agent | `BMAD-SRC-001..004` | Initialized spec normalization; build target filled; requirement registry + traceability pending | Complete `02-requirements-registry.md` and `06-traceability/traceability-matrix.md` before Story 1.1 implementation |

