# Project Pipeline

Single source of truth for the idea-to-delivery process.
**All agents must read this before any stage begins.**

---

## Pipeline at a Glance

| Stage | What Happens | Gate |
|---|---|---|
| **1. Idea Validation** | Validate the idea, select mode, produce handoff | Gate 1: Go / No-Go + mode confirmation |
| **2. BMAD** | Turn validated idea into PM artifacts | Gate 2: Build / No-Build + delivery path |
| **3. SDD** | Turn PM artifacts into implementation-ready specs | Pre-execution gate (see Stage 3) |
| **4a. Superpowers** | Software implementation (if software path) | Gate 3: Ship / Done |
| **4b. Document Delivery** | Structured document output (if non-software path) | Gate 3: Done |
| **Optional. Case Study** | Extract portfolio / LinkedIn / interview artifacts | User-triggered |

---

## Two Modes

Mode is selected during Stage 1 and declared in `agent-handoff.md`. It governs artifact requirements and research depth for every stage that follows.

Mode can be **upgraded** (lightweight → standard) if BMAD reveals greater scope than expected. Surface this at Gate 1 as a question — never change mode silently.

| | Lightweight | Standard |
|---|---|---|
| **Use for** | Portfolio demos, personal tools, AI utilities, quick builds, small GitHub projects | Startup ideas, serious product concepts, business-facing projects, anything requiring investment logic |
| **Product Brief** | Required | Required |
| **PRD** | Required — slim (MVP scope + core stories + non-goals) | Required — full |
| **Architecture** | Optional | Required if technical |
| **UX Spec** | Optional | Required if UI |
| **Epics & Stories** | Optional | Optional |
| **SDD** | Core files only (see Stage 3) | Full spec layer |
| **Research depth** | One pass, one page max | Full PRESTO + competitive + market |
| **Effort before code** | 2 documents max | 5 documents max |

---

## Stage 1: Idea Validation + Mode Selection

**Tool:** `validate-idea` skill
**Run from:** Project root
**Outputs to:** `docs/[idea-slug]/`

Validate the idea before any product or build work begins. This stage determines whether to proceed, how to proceed, and at what mode. The output feeds directly into BMAD.

### What Stage 1 produces

| File | Purpose |
|---|---|
| `docs/[idea-slug]/brief.md` | Human-readable validation summary |
| `docs/[idea-slug]/dossier.md` | Full research record |
| `docs/[idea-slug]/agent-handoff.md` | Structured handoff for BMAD — includes mode declaration |

### Mode declaration

`agent-handoff.md` must include a `mode` field before BMAD begins. If the `validate-idea` skill did not write this field, add it manually at Gate 1:

```yaml
mode: lightweight | standard
```

### Gate 1: Go / No-Go

Confirm all of the following before proceeding to Stage 2:

- [ ] `docs/[idea-slug]/agent-handoff.md` exists
- [ ] `verdict_business` is `go` or `investigate` — if `no-go`, stop and archive
- [ ] `mode` field is set to `lightweight` or `standard`
- [ ] Problem statement, target user, and value hypothesis are present
- [ ] If `investigate`: open questions are named explicitly, not left vague

**Human gate — stop here.** Present the validation brief and mode recommendation to the user. Wait for explicit confirmation of both the verdict and the selected mode before proceeding to Stage 2. Do not continue autonomously.

**If verdict is no-go:** Stop. Do not proceed to BMAD. Archive `docs/[idea-slug]/` for reference.
**If mode is uncertain:** Ask the user to confirm before proceeding.

---

## Stage 2: BMAD — Product Definition

**Tools:** `bmad-product-brief`, `bmad-prd`, `bmad-create-architecture`, `bmad-ux`, `bmad-create-epics-and-stories`
**Reads:** `docs/[idea-slug]/agent-handoff.md`
**Outputs to:** `docs/` (project root level — see routing table)

Turn the validated idea into PM artifacts. BMAD reads the handoff file for context and produces output appropriate to the declared mode. Artifacts land in `docs/` as flat files. Do not write BMAD artifacts anywhere else.

### Artifact requirements by mode

| Artifact | Lightweight | Standard |
|---|---|---|
| `docs/product-brief.md` | Required | Required |
| `docs/PRD.md` | Required (slim) | Required (full) |
| `docs/ARCHITECTURE.md` | Optional | Required if technical |
| `docs/UX.md` | Optional | Required if UI |
| `docs/epics-stories.md` | Optional | Optional |

### File routing — agents must write to these exact paths

| Artifact | Canonical path | BMAD skill |
|---|---|---|
| Product Brief | `docs/product-brief.md` | `bmad-product-brief` |
| PRD | `docs/PRD.md` | `bmad-prd` |
| Architecture | `docs/ARCHITECTURE.md` | `bmad-create-architecture` |
| UX / Design Spec | `docs/UX.md` | `bmad-ux` |
| Epics & Stories | `docs/epics-stories.md` | `bmad-create-epics-and-stories` |

**Do not write BMAD artifacts to any subdirectory, to the project root, or to any path not listed above.**

### Gate 2: Build / No-Build + Delivery Path

Confirm all of the following before proceeding to Stage 3:

- [ ] `docs/product-brief.md` contains real content, not placeholder text
- [ ] `docs/PRD.md` contains real content, not placeholder text
- [ ] All mode-required artifacts exist and are filled in
- [ ] Delivery path is declared: **software** (→ Stage 4a) or **document delivery** (→ Stage 4b)
- [ ] If building a demo or software: `docs/demo-charter.md` has been created (see Demo Charter below)

**Human gate — stop here.** Present the completed BMAD artifacts and checklist to the user. Wait for explicit confirmation of: (1) build or no-build decision, and (2) delivery path — software or document delivery. Do not proceed to Stage 3 autonomously.

**If required artifacts are missing:** Do not proceed. Complete them before continuing.
**If delivery path is unclear:** Ask the user to decide before Stage 3 begins.

### Demo Charter

If any software or demo output is planned, create `docs/demo-charter.md` before Stage 3. This is a single document that answers:

- Who is this demo for?
- What should the viewer understand in 30 seconds?
- What PM or product skill does this demonstrate?
- What is the core user flow?
- What must be real vs. what can be mocked?
- What would be misleading to fake?
- What does "professional enough" mean for this demo?
- What is explicitly not being built?

**Demo integrity rules (applies to all demos):**
- Mock data is allowed when clearly appropriate
- Simulated workflows are allowed if not misleading to the intended audience
- Fake AI output must be labeled if simulated
- Fake integrations must be disclosed
- Fake users, testimonials, traction, revenue, or customer claims must never be used

---

## Stage 3: SDD — Specification

**Reads:** `docs/` (BMAD outputs)
**Outputs to:** `docs/spec/`

Translate PM artifacts into implementation-ready specs. The spec layer answers: *could a coding agent implement this without inventing product decisions?* If the answer is no, the spec is not done.

### Lightweight — required spec files

| File | Purpose |
|---|---|
| `docs/spec/00-project-constitution.md` | Scope, identity, build target |
| `docs/spec/02-requirements-registry.md` | Canonical requirement IDs |
| `docs/spec/03-feature-specs/FEAT-001.md` | Core feature with acceptance criteria |
| `docs/spec/06-traceability/traceability-matrix.md` | Requirement → spec → test links |
| `docs/spec/08-test-specs/TEST-001.md` | Test expectations |

### Standard — full spec layer

All lightweight files, plus:

| File | Purpose |
|---|---|
| `docs/spec/01-bmad-intake.md` | BMAD normalization bridge |
| `docs/spec/04-design-specs/` | Interface and component contracts |
| `docs/spec/05-change-requests/` | Change tracking |
| `docs/spec/07-decisions/` | Architecture decision records |
| `docs/spec/09-known-issues/` | Bug and known issue tracking |

### Pre-execution gate

Do not hand off to Stage 4 until every applicable item is checked:

**Both modes:**
- [ ] `docs/PRD.md` — real content, not placeholder
- [ ] `docs/product-brief.md` — real content, not placeholder
- [ ] `docs/spec/00-project-constitution.md` — filled in, scope is explicit
- [ ] `docs/spec/02-requirements-registry.md` — at least one real requirement ID with acceptance criterion
- [ ] `docs/spec/03-feature-specs/FEAT-001.md` — real acceptance criteria and done-when criteria
- [ ] `docs/spec/06-traceability/traceability-matrix.md` — at least one row linking requirement to feature spec
- [ ] No open questions — anything unclear is resolved in the spec, not by the implementing agent

**Standard mode additionally:**
- [ ] `docs/ARCHITECTURE.md` — real content
- [ ] `docs/spec/01-bmad-intake.md` — normalization complete

**Human gate — stop here.** Present the completed spec and checklist to the user. Wait for explicit confirmation that the spec is approved for build before proceeding to Stage 4. Do not begin implementation autonomously.

---

## Stage 4a: Superpowers — Software Implementation

**Reads:** `docs/spec/`, `AGENTS.md`, `docs/demo-charter.md`
**Tool:** Superpowers (Claude Code)

Implementation using the Superpowers methodology: design confirmation → plan → TDD → review. The agent reads the spec and builds to it. If the spec is unclear on a product decision, the agent surfaces the question — it does not improvise.

**Do not modify Superpowers skill files.** They are maintained externally and will be overwritten by updates.

### Gate 3: Ship / Done

- [ ] Core user flow works end to end
- [ ] UI is visually consistent (if UI exists)
- [ ] Layout is responsive (if applicable)
- [ ] Empty, loading, and error states exist where needed
- [ ] Demo data is plausible and not misleading
- [ ] README explains what it is and how to run it
- [ ] Setup instructions work from a clean install
- [ ] Build passes
- [ ] Deployment works (if deployment is part of the goal)
- [ ] Known limitations are documented
- [ ] The demo communicates the intended PM or product skill
- [ ] Template files (`*-template.md`) deleted from all `docs/spec/` subdirectories — real content files are the only files that remain

---

## Stage 4b: Document Delivery — Non-Software Path

**Reads:** `docs/` (BMAD outputs), `docs/spec/` (if applicable)
**Outputs to:** `docs/output/`

For projects where the deliverable is analysis, strategy, a case study, or PM reasoning — not code. The final output is a set of structured documents rather than a working application.

### Typical outputs

| File | Purpose |
|---|---|
| `docs/output/analysis.md` | Core research and findings |
| `docs/output/recommendation.md` | Structured recommendation or strategy |
| `docs/output/case-study.md` | Narrative product analysis (if applicable) |
| `docs/output/decision-summary.md` | Key decisions and their rationale |

Adapt file names to the actual project. These are conventions, not mandates.

### Gate 3: Done

- [ ] Deliverable answers the question it set out to answer
- [ ] All major claims are labeled (sourced fact / observed evidence / reasoned inference / assumption / open question)
- [ ] No unsupported market, customer, competitor, revenue, or traction claims presented as fact
- [ ] Open questions are named explicitly
- [ ] Known limitations are documented

---

## Optional: Case Study Extraction

Available at the end of any project — Lightweight, Standard, software, or non-software. Triggered by the user, not automatic.

Uses the documentation already produced (brief, PRD, decisions, spec, demo) as raw material. Does not require new research.

### Typical outputs

- Portfolio case study
- GitHub README
- LinkedIn post
- Demo walkthrough notes
- Interview talking points
- Product decision summary

### Post-project learning prompts

After any completed project, consider:
- Did the demo or deliverable prove the intended point?
- Did implementation reveal product weaknesses?
- What would we change in the PRD?
- What would we cut?
- Is this portfolio-worthy, startup-worthy, or only a learning artifact?

---

## Full File Routing Table

| Artifact | Canonical path | Stage | Mode |
|---|---|---|---|
| Validation Brief | `docs/[idea-slug]/brief.md` | 1 | Both |
| Research Dossier | `docs/[idea-slug]/dossier.md` | 1 | Both |
| Agent Handoff | `docs/[idea-slug]/agent-handoff.md` | 1 | Both |
| Product Brief | `docs/product-brief.md` | 2 | Both |
| PRD | `docs/PRD.md` | 2 | Both |
| Architecture | `docs/ARCHITECTURE.md` | 2 | Standard (if technical) |
| UX / Design Spec | `docs/UX.md` | 2 | Standard (if UI) |
| Epics & Stories | `docs/epics-stories.md` | 2 | Optional |
| Demo Charter | `docs/demo-charter.md` | 2 | If demo/software |
| Project Constitution | `docs/spec/00-project-constitution.md` | 3 | Both |
| BMAD Intake | `docs/spec/01-bmad-intake.md` | 3 | Standard |
| Requirements Registry | `docs/spec/02-requirements-registry.md` | 3 | Both |
| Feature Specs | `docs/spec/03-feature-specs/` | 3 | Both |
| Design Specs | `docs/spec/04-design-specs/` | 3 | Standard |
| Change Requests | `docs/spec/05-change-requests/` | 3 | Standard |
| Traceability Matrix | `docs/spec/06-traceability/traceability-matrix.md` | 3 | Both |
| Decision Records | `docs/spec/07-decisions/` | 3 | Standard |
| Test Specs | `docs/spec/08-test-specs/` | 3 | Both |
| Known Issues | `docs/spec/09-known-issues/` | 3 | Standard |
| Document Output | `docs/output/` | 4b | Non-software |

---

## Handoff Contracts

### Stage 1 → Stage 2 (Validation → BMAD)

`docs/[idea-slug]/agent-handoff.md` must contain:

**Required:**
- `mode: lightweight | standard`
- `verdict_business: go | investigate`
- Problem statement (1–2 sentences)
- Target user
- Value hypothesis
- Top risk
- Research confidence level

**Minimum quality bar:** BMAD must be able to begin product definition without asking the user to re-explain the idea.

**Blocks progression:** Missing mode field, no-go verdict, absent problem statement or target user.

---

### Stage 2 → Stage 3 (BMAD → SDD)

`docs/` must contain:

**Required (both modes):**
- `docs/product-brief.md` — real content
- `docs/PRD.md` — real content including MVP scope and non-goals
- Delivery path declared (software or document)

**Required (standard, if applicable):**
- `docs/ARCHITECTURE.md`
- `docs/UX.md`

**Required (if any demo or software output planned):**
- `docs/demo-charter.md`

**Minimum quality bar:** The spec layer should be buildable from BMAD outputs alone. An agent reading `docs/PRD.md` should understand what to build and what not to build.

**Blocks progression:** Placeholder content in required files. Missing delivery path decision. Missing demo charter when software is planned.

---

### Stage 3 → Stage 4 (SDD → Delivery)

See **Pre-execution gate** in Stage 3. Every applicable checkbox must be cleared.

**Minimum quality bar:** An implementing agent reads the spec and has no product decisions left to make. All ambiguities are resolved in the spec or logged as known open items with an explicit owner.

**Blocks progression:** Any open question that would require the implementing agent to invent a product decision.

---

## Mid-Process Backflow Rule

When Stage 4 implementation reveals a product gap or scope problem:

1. **Stop implementation.** Do not work around the gap.
2. **Document the issue** — add a decision log entry or change request to `docs/spec/`.
3. **Route back** to the appropriate stage:
   - Spec gap → back to Stage 3 (SDD)
   - Requirements gap → back to Stage 2 (BMAD)
4. **Update the relevant artifact** at the stage you returned to.
5. **Resume Stage 4** from the updated spec.

Do not improvise product decisions during implementation. If the spec is silent on something that matters, surface it — do not guess.

---

## Evidence Standards

All research and analysis produced during any stage must label major claims as one of:

- **Sourced fact** — from a named, reputable source
- **Observed evidence** — from direct observation or primary data
- **Reasoned inference** — logical conclusion from sourced facts
- **Assumption** — believed to be true, not yet validated
- **Open question** — unknown, requires investigation

**Rules:**
- Use reputable sources. Prefer primary sources where possible.
- If a reputable source cannot be found, say so explicitly and move the claim to assumptions or open questions.
- Do not present unsupported market size, customer, competitor, revenue, or traction claims as fact.
- Cite sources. Document source limitations where relevant.
- Use "not found" rather than guessing.

---

## What Agents Must Not Do

- Write BMAD artifacts outside `docs/` at project root
- Modify BMAD skill files — they are maintained via external updates
- Modify Superpowers skill files — they are maintained via external updates
- Proceed past any gate without confirming required artifacts exist and contain real content
- Change the declared mode without surfacing the question to the user
- Improvise product decisions not present in the spec
- Present unsupported claims as facts in any research or analysis output
- Begin Stage 4 with open product questions unresolved in the spec
