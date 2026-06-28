# Traceability Matrix

Use this matrix to prove that each requirement has a spec, task, implementation, and verification path.

## Matrix

| Requirement ID | Source | Feature/design spec | Acceptance criteria | Tasks | Code/modules | Tests | Status |
|---|---|---|---|---|---|---|---|
| `ARCH-001` | `docs/spec/03-feature-specs/1-1-scaffold-project-structure.md` | `docs/spec/03-feature-specs/1-1-scaffold-project-structure.md` | `AC-001..AC-006` | `TASK-001` | `briefing/` scaffold + stubs | `TEST-001` | verified |
| `ARCH-002` | `docs/spec/03-feature-specs/1-2-core-configuration-module.md` | `docs/spec/03-feature-specs/1-2-core-configuration-module.md` | `AC-033..AC-038` | `TASK-002` | `briefing/app/core/config.py` | `TEST-002` | verified |
| `ARCH-003` | `docs/spec/03-feature-specs/1-3-database-models-and-async-sqlite.md` | `docs/spec/03-feature-specs/1-3-database-models-and-async-sqlite.md` | `AC-039..AC-044` | `TASK-003` | `briefing/app/db/{database.py,models.py}`, `briefing/app/main.py` | `TEST-003` | verified |
| `ARCH-004` | `docs/spec/03-feature-specs/1-4-credential-store-keyring-wrapper.md` | `docs/spec/03-feature-specs/1-4-credential-store-keyring-wrapper.md` | `AC-045..AC-050` | `TASK-004` | `briefing/app/core/credentials.py` | `TEST-004` | verified |
| `ARCH-005` | `docs/spec/03-feature-specs/1-5-error-types-stageerror.md` | `docs/spec/03-feature-specs/1-5-error-types-stageerror.md` | `AC-051..AC-055` | `TASK-005` | `briefing/app/core/errors.py`, `briefing/app/main.py` | `TEST-005` | verified |
| `FR-001` | `BMAD-SRC-002` | `docs/spec/03-feature-specs/2-1-gmail-oauth-authorization.md` | `AC-007` | `TASK-006` | `briefing/app/services/gmail.py`, `briefing/setup.py` | `TEST-006` | verified |
| `FR-002` | `BMAD-SRC-002` | `docs/spec/03-feature-specs/2-2-label-based-email-fetch.md` | `AC-008` | `TASK-007` | `briefing/app/services/gmail.py` | `TEST-007` | verified |
| `FR-003` | `BMAD-SRC-002` | `docs/spec/03-feature-specs/2-3-processed-log-management.md` | `AC-009` | `TASK-008` | `briefing/app/pipeline/orchestrator.py`, `briefing/app/api/settings.py`, `briefing/app/services/gmail.py` | `TEST-008` | verified |

## Coverage checklist

- [ ] Every P0 requirement has acceptance criteria.
- [ ] Every accepted requirement maps to at least one spec.
- [ ] Every accepted requirement maps to implementation tasks.
- [ ] Every accepted requirement maps to tests or an explicit manual verification method.
- [ ] Every bug fix has a regression test or documented exception.
- [ ] Every ADR maps to affected requirements or constraints.
- [ ] Deprecated and superseded requirements are not used for new work.

## Gaps

| Gap ID | Missing link | Impact | Owner | Due date |
|---|---|---|---|---|
| `GAP-001` |  |  |  |  |

