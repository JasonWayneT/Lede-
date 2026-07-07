"""FastAPI web UI entry point."""

# Implements ARCH-003

import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import briefings, downloads, settings, setup as setup_mod, stream
from app.core.config import AppConfig
from app.core.errors import StageError
from app.core import scheduler as sched_mod
from app.db.database import build_sqlite_db_url, init_db, init_engine

_HERE = Path(__file__).parent  # briefing/app/
templates = Jinja2Templates(directory=str(_HERE / "templates"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    config = AppConfig()
    config.data_dir.mkdir(parents=True, exist_ok=True)
    init_engine(build_sqlite_db_url(config.data_dir))
    await init_db()

    sched_mod.check_daemon_alive(config)

    import json
    settings_path = Path(config.data_dir) / "settings.json"
    stored: dict = {}
    if settings_path.exists():
        try:
            stored = json.loads(settings_path.read_text())
        except Exception:
            pass
    cadence = stored.get("cadence", "off")
    time_str = stored.get("schedule_time", "07:00")
    if cadence != "off":
        sched_mod.schedule_run(cadence, time_str, config)
    sched_mod.scheduler.start()

    missed = await sched_mod.check_missed_runs(config)
    if missed:
        import asyncio
        from app.pipeline import orchestrator
        run_id = await orchestrator.start_run(config)
        asyncio.create_task(orchestrator.run_pipeline(run_id, config))

    yield

    sched_mod.scheduler.shutdown(wait=False)


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(_HERE / "static")), name="static")

app.include_router(briefings.router, prefix="/api")
app.include_router(downloads.router, prefix="/api")
app.include_router(settings.router)
app.include_router(stream.router, prefix="/api")
app.include_router(setup_mod.router)


@app.exception_handler(StageError)
async def handle_stage_error(_, exc: StageError):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "code": exc.code,
            "stage": exc.stage_name,
            "retryable": exc.retryable,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    from app.api.setup import is_onboarding_complete
    import json

    config = AppConfig()
    if not is_onboarding_complete(config):
        return RedirectResponse("/setup")

    # Check for active run
    from sqlalchemy import select
    from app.db.database import get_session
    from app.db.models import Run
    async with get_session() as session:
        result = await session.execute(select(Run).where(Run.status == "running"))
        active_run = result.scalars().first()
    run_active = active_run is not None

    # Implements BUG-006 — surface a held (failed, awaiting retry) run on the dashboard itself,
    # not just on History, so a failure like "Ollama unreachable" isn't silently invisible.
    hold_run = None
    async with get_session() as session:
        result = await session.execute(
            select(Run).where(Run.status == "hold").order_by(Run.created_at.desc(), Run.id.desc())
        )
        held = result.scalars().first()
        if held:
            hold_run = {"run_id": held.id, "error": held.error}

    # BUG-011 (9-3/AC-1): surface a missed scheduled run on the dashboard instead of retrying
    # silently in the background with no visible signal to the user.
    missed_run = None
    missed_at = await sched_mod.check_missed_runs(config)
    if missed_at:
        # %I/%p is portable across platforms; %-I (no leading zero) is not (glibc-only).
        missed_at_display = missed_at.strftime("%I:%M %p").lstrip("0")
        missed_run = {"missed_at_display": missed_at_display, "retrying": run_active}

    # Load schedule info for status bar
    settings_path = Path(config.data_dir) / "settings.json"
    stored: dict = {}
    if settings_path.exists():
        try:
            stored = json.loads(settings_path.read_text())
        except Exception:
            pass

    # Latest complete briefing for inline reading view
    briefing_data = await _get_latest_briefing(config)

    return templates.TemplateResponse(request, "dashboard.html", {
        "active_page": "dashboard",
        "run_active": run_active,
        "hold_run": hold_run,
        "missed_run": missed_run,
        "feed_name": config.gmail_label or "Inbox",
        "briefing": briefing_data,
        "cadence": stored.get("cadence", "off"),
        "schedule_time": stored.get("schedule_time", "07:00"),
    })


@app.get("/archive", response_class=HTMLResponse)
async def archive_page(request: Request):
    from sqlalchemy import select
    from app.db.database import get_session
    from app.db.models import Run, BriefingOutput
    from app.core.config import AppConfig as _AC

    config = _AC()
    async with get_session() as session:
        result = await session.execute(
            select(Run, BriefingOutput)
            .outerjoin(BriefingOutput, BriefingOutput.run_id == Run.id)
            .order_by(Run.created_at.desc())
        )
        rows = result.all()

    briefing_list = []
    for run, output in rows:
        md_path = Path(output.markdown_path) if output and output.markdown_path else None
        title = _extract_title(md_path)
        briefing_list.append({
            "run_id": run.id,
            "date": run.created_at.isoformat() if run.created_at else None,
            "date_display": _fmt_date(run.created_at),
            "status": run.status,
            "error": run.error,
            "title": title,
            "markdown_path": output.markdown_path if output else None,
            "audio_path": output.audio_path if output else None,
        })

    return templates.TemplateResponse(request, "archive.html", {
        "active_page": "archive",
        "briefings": briefing_list,
        "feed_name": config.gmail_label or "Inbox",
    })


# Keep /history as alias so existing links don't break
@app.get("/history", response_class=HTMLResponse)
async def history_redirect(request: Request):
    return RedirectResponse("/archive")


@app.get("/oauth/callback", response_class=HTMLResponse)
async def oauth_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    from app.services import gmail

    if error or not code:
        return RedirectResponse("/setup/step/1?error=access_denied")

    config = AppConfig()
    try:
        gmail.exchange_code(code, state or "", config)
    except Exception as e:
        return RedirectResponse(f"/setup/step/1?error={str(e)[:80]}")

    return RedirectResponse("/setup/step/2")


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    import json
    from app.core import credentials

    config = AppConfig()
    token_json = credentials.get(credentials.GMAIL_OAUTH_TOKEN)
    oauth_status = "not_authorized"
    authorized_email = None
    if token_json:
        oauth_status = "authorized"
        try:
            authorized_email = json.loads(token_json).get("email")
        except Exception:
            pass

    settings_path = Path(config.data_dir) / "settings.json"
    stored = {}
    if settings_path.exists():
        try:
            stored = json.loads(settings_path.read_text())
        except Exception:
            pass

    provider = config.llm_provider
    cred_key = {
        "openai": credentials.OPENAI_KEY,
        "anthropic": credentials.ANTHROPIC_KEY,
        "gemini": credentials.GEMINI_KEY,
    }.get(provider)
    api_key_raw = credentials.get(cred_key) if cred_key else None
    model_map = {
        "ollama": config.ollama_model_name,
        "openai": config.openai_model_name,
        "anthropic": config.anthropic_model_name,
        "gemini": config.gemini_model_name,
    }

    from app.services.tts import cuda_available
    return templates.TemplateResponse(request, "settings.html", {
        "active_page": "settings",
        "gmail_label": config.gmail_label,
        "lookback_days": stored.get("lookback_days", "7"),
        "oauth_status": oauth_status,
        "authorized_email": authorized_email,
        "briefing_depth": config.briefing_depth,
        "llm_provider": provider,
        "llm_model_name": model_map.get(provider, ""),
        "api_key_masked": _mask_key(api_key_raw) if api_key_raw else None,
        "tts_engine": stored.get("tts_engine", config.tts_engine),
        "tts_voice": stored.get("tts_voice", "af_heart"),
        "cuda_available": cuda_available(),
        "cadence": stored.get("cadence", "off"),
        "schedule_time": stored.get("schedule_time", "07:00"),
        "schedule_day_of_week": stored.get("day_of_week", "mon"),
        "next_run": None,
        "daemon_mode": stored.get("daemon_mode", False),
    })


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _get_latest_briefing(config: AppConfig) -> dict | None:
    from sqlalchemy import select
    from app.db.database import get_session
    from app.db.models import Run, BriefingOutput

    async with get_session() as session:
        result = await session.execute(
            select(Run, BriefingOutput)
            .outerjoin(BriefingOutput, BriefingOutput.run_id == Run.id)
            .where(Run.status == "complete")
            .order_by(Run.created_at.desc())
            .limit(1)
        )
        row = result.first()

    if not row:
        return None

    run, output = row
    md_path = Path(output.markdown_path) if output and output.markdown_path else None
    md_content = md_path.read_text(encoding="utf-8") if md_path and md_path.exists() else ""
    parsed = _parse_briefing_md(md_content)

    source_count = sum(
        len([s for s in sec.get("source", "").split(",") if s.strip()])
        for sec in parsed["sections"]
    )
    word_count = sum(
        len(" ".join(sec.get("paragraphs", [])).split())
        for sec in parsed["sections"]
    )
    read_minutes = max(1, round(word_count / 200))

    return {
        "run_id": run.id,
        "date": run.created_at,
        "date_display": _fmt_date(run.created_at),
        "title": parsed["title"],
        "sections": parsed["sections"],
        "source_count": source_count or len(parsed["sections"]),
        "read_minutes": read_minutes,
        "audio_path": output.audio_path if output else None,
        "markdown_path": output.markdown_path if output else None,
    }


def _parse_briefing_md(md_text: str) -> dict:
    """Parse pipeline briefing markdown into structured sections."""
    sections = []
    title = ""
    lines = (md_text or "").strip().split("\n")
    current: dict | None = None

    for line in lines:
        s = line.strip()
        if s.startswith("# ") and not title:
            title = s[2:].strip()
        elif s.startswith("## "):
            if current is not None:
                sections.append(current)
            current = {"title": s[3:].strip(), "paragraphs": [], "source": ""}
        elif current is not None:
            if s.startswith(">") or ("source" in s.lower() and s.startswith("*")):
                src = s.lstrip(">*_ ")
                src = re.sub(r"^sources?:\s*", "", src, flags=re.IGNORECASE).strip().rstrip("*_")
                current["source"] = src
            elif s:
                current["paragraphs"].append(s)

    if current is not None:
        sections.append(current)

    return {"title": title or "Your Briefing", "sections": sections}


def _extract_title(md_path: Path | None) -> str:
    if not md_path or not md_path.exists():
        return "Briefing"
    try:
        for line in md_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except Exception:
        pass
    return "Briefing"


def _fmt_date(dt) -> str:
    if not dt:
        return ""
    try:
        return dt.strftime("%A, %B %-d")
    except Exception:
        try:
            return dt.strftime("%A, %B %d").replace(" 0", " ")
        except Exception:
            return str(dt)[:10]


def _mask_key(key: str) -> str:
    if not key:
        return None
    if len(key) <= 6:
        return "***"
    return key[:3] + "..." + key[-3:]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
