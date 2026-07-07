# Implementation Patterns

Captures the recurring patterns established during the MVP build.
Reference this before adding features or refactoring — the goal is consistency, not cleverness.

---

## 1. Pipeline stage pattern

Every pipeline stage is a standalone async function in `briefing/app/pipeline/stages/`.

**Signature:**
```python
async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    ...
```

**Rules:**
- Stages receive a `HandoffPacket`, mutate it, and return it
- Raise `StageError(code, stage_name, retryable=True/False)` on failure — never raise raw exceptions
- Retryable errors (transient network, model timeout) set `retryable=True`; logic errors set `retryable=False`
- No stage writes to the DB directly — the orchestrator handles run state

**Orchestrator wiring** (`briefing/app/pipeline/orchestrator.py`):
```python
STAGES = [ingest, extract, embed, cluster, select, frame, draft, assemble, tts_prep]
```
Add new stages by appending to this list. Order matters — each stage reads fields the previous one wrote.

---

## 2. HandoffPacket schema

Defined in `briefing/app/pipeline/handoff.py`. It is the single data contract between stages.

**Key fields:**
| Field | Written by | Read by |
|---|---|---|
| `emails` | ingest | extract |
| `articles` | extract | embed, select |
| `embeddings` | embed | cluster |
| `clusters` | cluster | select |
| `selected` | select | frame |
| `frame` | frame | draft |
| `sections` | draft | assemble |
| `briefing_md` | assemble | tts_prep, DB write |
| `audio_path` | tts_prep | DB write |

Never pass data between stages through the database or global state — always through the packet.

---

## 3. SSE streaming pattern

Live pipeline progress is delivered via Server-Sent Events from `/api/stream/{run_id}`.

**Backend** (`briefing/app/api/stream.py`):
- Each stage emits `{"stage": "...", "status": "started"|"complete"|"error"}` events to a per-run asyncio queue
- The SSE endpoint reads from the queue and streams to the browser
- On pipeline complete or error, a final `{"event": "done"}` closes the connection

**Frontend** (`briefing/app/templates/dashboard.html`):
- JS opens `EventSource('/api/stream/{run_id}')` after triggering a run
- Stage names are mapped to friendly labels via a JS object:
  ```js
  const STAGE_LABELS = { ingest: "Fetching your newsletters…", extract: "Reading content…", ... }
  ```
- Pips (10 total) fill left-to-right as stages complete; page reloads on `done`

To add a new stage: add it to `STAGE_LABELS` in `dashboard.html` and to `STAGES` in the orchestrator.

---

## 4. Route and template pattern

**Routes** live in `briefing/app/main.py` (page routes) and `briefing/app/api/` (API routes).

**Template resolution:** always use absolute paths derived from `__file__`:
```python
_HERE = Path(__file__).parent
templates = Jinja2Templates(directory=str(_HERE / "templates"))
```
Never use relative paths — the app is launched from a different CWD than the module.

**Active nav state:** every page route passes `active_page` to the template context:
```python
return templates.TemplateResponse(request, "page.html", {"active_page": "settings", ...})
```
`base.html` uses this to highlight the correct sidebar nav item.

**Partials:** reusable HTML fragments live in `briefing/app/templates/partials/` and are included with `{% include %}`. Current partials: `briefing_reading_view.html`.

---

## 5. Settings persistence pattern

User settings are stored in two places:

| What | Where |
|---|---|
| Gmail OAuth token, API keys | OS keyring via `briefing/app/core/credentials.py` |
| UI preferences (cadence, depth, TTS engine) | `{data_dir}/settings.json` |

**Reading settings:**
```python
settings_path = Path(config.data_dir) / "settings.json"
stored = json.loads(settings_path.read_text()) if settings_path.exists() else {}
value = stored.get("key", default)
```

**Writing settings** is handled by API routes in `briefing/app/api/settings.py` via HTMX PUT requests. Forms use `hx-on::after-request="showFeedback(this, event)"` for inline save confirmation.

Never add a new setting directly to `AppConfig` if it can live in `settings.json` — config is for environment/deployment values; settings.json is for user preferences.

---

## 6. Database pattern

Async SQLite via SQLAlchemy. Two models: `Run` and `BriefingOutput`.

**Session usage:**
```python
from app.db.database import get_session
async with get_session() as session:
    result = await session.execute(select(Run).where(...))
```

**Run lifecycle:** `queued` → `running` → `complete` | `hold` (partial failure, retryable) | `failed`

`BriefingOutput` is created once per run when the pipeline completes. It holds paths to the markdown and audio files — files live in `{data_dir}/`, paths in the DB are absolute.

---

## 7. Design system

Defined in `briefing/app/static/css/theme.css`. Based on Material Design 3 tonal surface hierarchy + 8pt grid.

**Key tokens:**
| Token | Value | Use |
|---|---|---|
| `--bg-canvas` | `#f5f4f0` | Page background |
| `--bg-surface` | `#faf9f5` | Sidebar, audio bar, cards |
| `--bg-overlay` | `#ffffff` | Feed bar, modals |
| `--accent` | `#c96442` | CTA buttons, active nav, hero widget only |
| `--font-editorial` | Playfair Display | Briefing content headings only |
| `--font-ui` | Inter | All UI chrome |

**7-rule rubric** (enforced on all UI work):
1. One surface token per elevation level — adjacent persistent elements share `--bg-surface`
2. 8pt grid — all spacing multiples of 4px; component heights 32/40/48/56/64px
3. Borders OR shadows, never both on the same element
4. Two typefaces, strict zones — Playfair = content only; Inter = UI chrome
5. One accent, three uses max
6. Semantic colors = status only (green=complete, amber=hold, red=failed)
7. Interactive targets ≥40px (icon-only ≥36px)

---

## 8. MCP server pattern

The MCP server (`briefing/app/mcp_server.py`) is a separate entry point — it does not share the FastAPI app instance.

It exposes four tools: `trigger_briefing`, `get_run_status`, `list_briefings`, `get_briefing_content`.

Each tool initializes its own `AppConfig` and database session. This keeps the MCP server stateless and safe to run alongside or independently of the web UI.

To add a new MCP tool: register it in `mcp_server.py` with `@mcp.tool()` and use the same async session pattern as existing tools.

---

## 9. Source-text budgeting pattern

Any stage that builds an LLM prompt from newsletter/article source text should go through
`briefing/app/services/condense.py` instead of slicing `entry["text"]` with a hard character
limit directly.

**Why:** frame and draft used to each truncate source text independently (300 vs 500 chars) —
inconsistent, and small enough that drafted stories read as headline teasers rather than real
explanations. See `docs/spec/07-decisions/ADR-001.md` for the full rationale.

**Usage:**
```python
from app.services import condense

source_texts = await condense.get_source_texts(cluster, config)  # list[str], one per cluster entry, same order
```

- Text under `condense.SOURCE_TEXT_BUDGET_CHARS` (4000) passes through unmodified — no LLM call.
- Text over budget is split on sentence boundaries (never mid-sentence) and run through an
  extraction-only prompt per chunk (`pipeline_prompts/stages/condense.md`); the concatenated
  extracted facts are returned. This is a single map pass — condense.py never runs a separate
  reduce/merge LLM call; whichever stage consumes the result is expected to do that synthesis.
- If one stage already computed `source_texts` for a cluster (frame does, storing it on the framed
  story dict), a later stage (draft) should read that field directly rather than calling
  `condense.get_source_texts()` again — avoids a duplicate condensation pass on the same source.
