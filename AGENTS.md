# Agent Operating Rules

Read this file in full before touching anything in this repository.
Then read `PIPELINE.md` — it defines the full process: stages, modes, gates, file routing, and handoff contracts.

## The build pipeline

Every project follows the same methodology:

```
Idea Validation → BMAD → docs/spec/ → Superpowers or Document Delivery
```

**Idea Validation** determined whether to build this and at what mode. Its outputs live in `docs/[idea-slug]/`. The `agent-handoff.md` file there is the upstream context for BMAD.

**BMAD** produces the product thinking — brief, PRD, and conditionally architecture, UX, and epics. These land in `docs/` and are upstream of your work. Do not reinterpret them.

**docs/spec/** is your primary working document set. It defines requirements, components, interfaces, constraints, and testing criteria. If docs/spec/ and a BMAD doc conflict, docs/spec/ takes precedence — flag the conflict but proceed per the spec.

**Superpowers** governs execution. Follow its methodology: confirmed design → written plan → TDD implementation → review. Do not skip stages.

---

## Prime directive

Do not edit code first. Every material change must begin with the documentation chain:

1. Review the project constitution
2. Review BMAD intake and existing requirements
3. Identify or create the relevant requirement IDs
4. Update feature, design, test, bug, or change specs as needed
5. Update the traceability matrix
6. Create or update implementation tasks
7. Modify code
8. Run verification
9. Update docs with results and unresolved issues

If the requested change is tiny, use lightweight mode — but still maintain requirement IDs and traceability.

**If any document is missing or incomplete: stop and flag it. Do not infer what it would say.**

---

## Required reading order

Before coding, read these files in order when they exist:

1. `PIPELINE.md` — full pipeline, modes, file routing, and handoff contracts
2. `docs/spec/00-project-constitution.md`
3. `docs/spec/01-bmad-intake.md`
4. `docs/spec/02-requirements-registry.md`
5. Relevant files under `docs/spec/03-feature-specs/`
6. Relevant files under `docs/spec/04-design-specs/`
7. Relevant files under `docs/spec/05-change-requests/`
8. `docs/spec/06-traceability/traceability-matrix.md`
9. Relevant ADRs under `docs/spec/07-decisions/`
10. Relevant test specs under `docs/spec/08-test-specs/`
11. Relevant known issues under `docs/spec/09-known-issues/`

If a file does not exist because the project is lightweight, continue with the available files.

---

## Document locations

### Validation documents (upstream — do not edit)

| Document | Location | Purpose |
|---|---|---|
| Validation brief | `docs/[idea-slug]/brief.md` | Human-readable validation summary |
| Research dossier | `docs/[idea-slug]/dossier.md` | Full research record |
| Agent handoff | `docs/[idea-slug]/agent-handoff.md` | BMAD context — mode, verdict, problem, user |

### BMAD source documents (upstream — do not edit after pasting)

| Document | Location | Purpose |
|---|---|---|
| Product brief | `docs/product-brief.md` | Vision and scope from BMAD |
| PRD | `docs/PRD.md` | Full product requirements from BMAD |
| Architecture | `docs/ARCHITECTURE.md` | Architecture decisions from BMAD (if technical) |
| UX / Design spec | `docs/UX.md` | UI and interaction design from BMAD (if UI) |
| Epics & stories | `docs/epics-stories.md` | Work breakdown from BMAD (if produced) |
| Demo charter | `docs/demo-charter.md` | Demo scope, integrity rules, done criteria (if demo/software) |

### Spec layer (working documents — agents operate here)

| Document | Location | Purpose |
|---|---|---|
| Project constitution | `docs/spec/00-project-constitution.md` | Project scope, operating mode, constraints |
| BMAD intake | `docs/spec/01-bmad-intake.md` | Bridge — BMAD outputs normalized into the spec system |
| Requirements registry | `docs/spec/02-requirements-registry.md` | Canonical requirement IDs — source of truth |
| Feature specs | `docs/spec/03-feature-specs/` | Per-feature requirements and acceptance criteria |
| Design specs | `docs/spec/04-design-specs/` | Design decisions |
| Change requests | `docs/spec/05-change-requests/` | Every material change tracked as a CR |
| Traceability matrix | `docs/spec/06-traceability/traceability-matrix.md` | Requirement → spec → code → status |
| Architecture decisions | `docs/spec/07-decisions/` | ADRs — why things are built the way they are |
| Test specs | `docs/spec/08-test-specs/` | What tests prove and how to run them |
| Known issues | `docs/spec/09-known-issues/` | Bugs and regressions with mitigation |
| CHANGELOG | `PRODUCT_CAPABILITIES_AND_RELEASE_NOTES.md` | Release history |

**The rule:** BMAD docs in `docs/` are the upstream source. `docs/spec/` is where agents work. If they conflict, `docs/spec/` takes precedence — flag the conflict, do not silently reconcile it.

---

## Requirement ID namespaces

Every code change must cite at least one requirement ID in the task description and implementation summary. Valid namespaces:

| Prefix | Meaning |
|---|---|
| `FR-*` | Functional requirement |
| `NFR-*` | Non-functional requirement |
| `UX-*` | User experience requirement |
| `DES-*` | Visual or interaction design requirement |
| `ARCH-*` | Architecture requirement |
| `DATA-*` | Data, schema, retention, import, or export requirement |
| `SEC-*` | Security, privacy, auth, permissions, or compliance requirement |
| `INT-*` | Integration requirement |
| `OPS-*` | Deployment, observability, reliability, or operations requirement |
| `AC-*` | Acceptance criterion |
| `TASK-*` | Implementation task |
| `TEST-*` | Test case or verification requirement |
| `BUG-*` | Known bug, regression, or defect |
| `ADR-*` | Architecture decision record |
| `CR-*` | Change request |

Do not reuse an ID for a different meaning. Do not delete an ID without recording a replacement or deprecation.

---

## Change workflow

When asked for a change:

1. Restate the requested change in implementation-neutral language
2. Determine whether this is a feature, bug fix, refactor, design change, architecture change, or documentation-only change
3. Create or update a `CR-*` entry in `docs/spec/05-change-requests/`
4. Identify affected requirement IDs
5. If no requirement exists, propose a new requirement ID
6. Update acceptance criteria
7. Update design, architecture, UX, data, security, and test specs only if affected
8. Update the traceability matrix
9. Produce an implementation task list
10. Implement the smallest safe change
11. Run relevant tests or explain why tests could not be run
12. Update the change request with the verification result

---

## Bug fix workflow

1. Create or update a `BUG-*` record in `docs/spec/09-known-issues/`
2. Link it to affected `FR-*`, `NFR-*`, `UX-*`, `DATA-*`, `SEC-*`, or `ARCH-*` IDs
3. Add a regression acceptance criterion
4. Add or update a `TEST-*` case in `docs/spec/08-test-specs/`
5. Fix the bug
6. Verify the regression test fails before the fix and passes after

---

## Refactor workflow

1. Link the refactor to an `ARCH-*`, `NFR-*`, `OPS-*`, or `ADR-*` ID
2. State unchanged external behavior
3. Identify tests that prove behavior did not change
4. Implement in small steps
5. Update design docs only if the architecture actually changed

---

## Design phase

Before writing any code for a feature, complete the following and present for PM approval. Do not proceed to implementation until the PM approves.

**What the agent produces:**

1. **Build Target** — fill in the Build Target table in `docs/spec/00-project-constitution.md` by reading `docs/ARCHITECTURE.md` and `docs/PRD.md`. This defines the exact deliverable: language, runtime, entry point, distribution.

2. **Component breakdown** — fill in the Component breakdown section of the relevant `FEAT-*.md`. Break the feature into discrete, independently buildable units. Order them by build sequence. For each component: state inputs, outputs, specific behaviors, and done-when criteria as checkboxes.

3. **Interface contracts** — if any two components pass data to each other, create a `docs/spec/04-design-specs/DESIGN-*.md` defining the contract: the shape of the data, what the producer guarantees, what the consumer can depend on.

**What the PM approves:**

- Build Target: does this match what I asked BMAD to build?
- Component sequence: does the build order make sense?
- Done-when criteria: do these match the acceptance criteria I wrote?
- Open questions: are there any questions the agent flagged that I need to resolve?

**The rule:** if the PM has not approved the component breakdown, the agent has not been authorized to write code. A design that looks plausible is not an approved design.

---

## Coding standards

If not explicitly documented below, discover conventions from the existing codebase and dependency files before writing any code. Document what you find here so future sessions don't re-derive them.

### General

- YAGNI — build only what is specified in the docs/spec/
- DRY — do not duplicate logic
- Simple over clever — readable beats elegant
- All code changes satisfying a requirement must include an inline comment citing the requirement ID (e.g. `// Implements FR-001`)
- No dependencies not listed in the project's dependency file — flag before adding any

### Language-specific

> Discover from the codebase on first run (package.json, tsconfig.json, pyproject.toml, .eslintrc, etc.) and document here. If starting greenfield, Superpowers spec elicitation will establish these before code begins.

---

## Testing standards

Tests are not optional and are not written after the fact.

1. Read the done criteria for the component you are building
2. Write failing tests against those criteria
3. Watch them fail
4. Write minimum code to pass
5. Watch them pass
6. Commit

### Test runner and commands

> Discover from the codebase on first run (package.json scripts, Makefile, pytest.ini, etc.) and document here. If starting greenfield, Superpowers spec elicitation will establish these before code begins.

### Done criteria (per component)

A component is complete when:
- [ ] All unit tests pass
- [ ] Integration or smoke tests pass
- [ ] Implementation notes updated in the relevant spec file
- [ ] No unresolved issues in the change request

---

## CHANGELOG format

All significant changes are appended to `CHANGELOG.md` before or immediately after a push. Projects may rename this file (e.g. `PRODUCT_CAPABILITIES_AND_RELEASE_NOTES.md`) — update this reference if so.

```
## [Version] — [Date]
[DRAFT] [Plain-language summary of what this version is and what changed.
        Written for a non-technical reader. Human reviews and finalizes before commit.]

### New
- [Feature or component]: what the user can now do

### Fixed
- [BUG-ID]: what was broken and what changed

### Changed
- [Component or CR-ID]: what changed and why

### Developer
- [CR-ID]: internal change, not user-visible
```

Mark new entries `[DRAFT]` until reviewed. Remove the `[DRAFT]` tag only after human sign-off.

---

## Handling ambiguity and blockers

**Ambiguity:** Stop. Check the spec files first. If still unclear, surface the question — state what you were trying to do, what is ambiguous, and what the options are. Do not interpret. Do not assume.

**Blockers:** State the blocker clearly. Do not work around it silently. Do not proceed to the next component while a blocker is unresolved unless explicitly told to skip it.

The cost of a clarifying question is always lower than the cost of building the wrong thing.

---

## Prohibited behavior

Agents must not:

- Invent requirements silently
- Delete requirement IDs without recording a replacement or deprecation
- Implement a feature that has no acceptance criteria
- Refactor across unrelated areas without a linked requirement or ADR
- Mark a task complete without verification notes
- Treat generated code as the source of truth when docs disagree
- Add dependencies not listed in the project's dependency file
- Skip tests
- Commit directly to main

---

## Output format for agent work

When finished with any task, report:

- Requirements touched (`FR-*`, `NFR-*`, `AC-*`, etc.)
- Specs updated (which files in `docs/spec/`)
- Code files changed
- Tests run and result
- Traceability matrix updated: yes / no / not applicable
- Open questions or risks
