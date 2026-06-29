"""Settings CRUD routes."""

# Implements FR-003, ARCH-001

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import delete

from app.core import credentials
from app.core.config import AppConfig
from app.db.database import get_session
from app.db.models import ProcessedEmail

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_config_singleton: AppConfig | None = None


def get_config() -> AppConfig:
    global _config_singleton
    if _config_singleton is None:
        _config_singleton = AppConfig()
    return _config_singleton


def _settings_path(config: AppConfig) -> Path:
    return Path(config.data_dir) / "settings.json"


def _load_settings(config: AppConfig) -> dict:
    p = _settings_path(config)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}
    return {}


def _save_settings(config: AppConfig, data: dict) -> None:
    p = _settings_path(config)
    p.parent.mkdir(parents=True, exist_ok=True)
    existing = _load_settings(config)
    existing.update(data)
    p.write_text(json.dumps(existing, indent=2))


def _mask_key(key: str) -> str:
    if not key:
        return None
    if len(key) <= 6:
        return "***"
    return key[:3] + "..." + key[-3:]


# ---------------------------------------------------------------------------
# Processed log (Story 2.3)
# ---------------------------------------------------------------------------

@router.delete("/processed-log")
async def clear_processed_log():
    async with get_session() as session:
        async with session.begin():
            result = await session.execute(delete(ProcessedEmail))
            rows_deleted = result.rowcount or 0
    return {"data": {"cleared": True, "rows_deleted": rows_deleted}}


# ---------------------------------------------------------------------------
# Gmail settings (Stories 8.4)
# ---------------------------------------------------------------------------

@router.get("/gmail")
async def get_gmail_settings(config: AppConfig = Depends(get_config)):
    token_json = credentials.get(credentials.GMAIL_OAUTH_TOKEN)
    oauth_status = "not_authorized"
    authorized_email = None
    if token_json:
        oauth_status = "authorized"
        try:
            token_data = json.loads(token_json)
            authorized_email = token_data.get("email")
        except Exception:
            pass
    return {"data": {"label": config.gmail_label, "oauth_status": oauth_status, "authorized_email": authorized_email}}


@router.put("/gmail")
async def update_gmail_label(
    label: str = Form("Newsletters"),
    lookback_days: str = Form("7"),
    config: AppConfig = Depends(get_config),
):
    config.gmail_label = label
    _save_settings(config, {"gmail_label": label, "lookback_days": lookback_days})
    return {"data": {"label": label, "lookback_days": lookback_days}}


@router.get("/gmail/authorize-redirect")
async def authorize_redirect(config: AppConfig = Depends(get_config)):
    from app.services import gmail
    from fastapi.responses import RedirectResponse
    try:
        auth_url = gmail.build_auth_url(config)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return RedirectResponse(auth_url)


@router.post("/gmail/reauthorize")
async def reauthorize_gmail(config: AppConfig = Depends(get_config)):
    from app.services import gmail
    from fastapi.responses import RedirectResponse
    try:
        auth_url = gmail.build_auth_url(config)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return RedirectResponse(auth_url, status_code=303)


# ---------------------------------------------------------------------------
# Sections settings (Story 8.5)
# ---------------------------------------------------------------------------

class SectionsBody(BaseModel):
    sections: list[str]


@router.get("/sections")
async def get_sections(config: AppConfig = Depends(get_config)):
    return {"data": {"sections": config.sections}}


@router.put("/sections")
async def update_sections(body: SectionsBody, config: AppConfig = Depends(get_config)):
    secs = [s.strip() for s in body.sections if s.strip()]
    non_other = [s for s in secs if s != "Other"]
    if not non_other:
        raise HTTPException(status_code=400, detail="At least one section is required")
    # "Other" always last
    if "Other" in secs:
        secs = [s for s in secs if s != "Other"] + ["Other"]
    else:
        secs = secs + ["Other"]
    config.sections = secs
    _save_settings(config, {"sections": secs})
    return {"data": {"sections": secs}}


# ---------------------------------------------------------------------------
# Depth settings (Story 8.6)
# ---------------------------------------------------------------------------

class DepthBody(BaseModel):
    briefing_depth: str


@router.get("/depth")
async def get_depth(config: AppConfig = Depends(get_config)):
    return {"data": {"briefing_depth": config.briefing_depth}}


@router.put("/depth")
async def update_depth(body: DepthBody, config: AppConfig = Depends(get_config)):
    valid = {"brief", "standard", "deep"}
    if body.briefing_depth not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid depth. Must be one of: {sorted(valid)}")
    config.briefing_depth = body.briefing_depth
    _save_settings(config, {"briefing_depth": body.briefing_depth})
    return {"data": {"briefing_depth": body.briefing_depth}}


# ---------------------------------------------------------------------------
# LLM provider settings (Story 8.6)
# ---------------------------------------------------------------------------

_provider_key_map = {
    "openai": credentials.OPENAI_KEY,
    "anthropic": credentials.ANTHROPIC_KEY,
    "gemini": credentials.GEMINI_KEY,
}


@router.get("/llm")
async def get_llm_settings(config: AppConfig = Depends(get_config)):
    provider = config.llm_provider
    cred_key = _provider_key_map.get(provider)
    api_key_raw = credentials.get(cred_key) if cred_key else None
    return {"data": {
        "provider": provider,
        "model_name": _model_name_for(config),
        "api_key_set": bool(api_key_raw),
        "api_key_masked": _mask_key(api_key_raw) if api_key_raw else None,
    }}


class LLMBody(BaseModel):
    provider: str | None = None
    model_name: str | None = None
    api_key: str | None = None


@router.put("/llm")
async def update_llm(body: LLMBody, config: AppConfig = Depends(get_config)):
    valid = {"ollama", "openai", "anthropic", "gemini", "mcp_sampling"}
    if body.provider and body.provider not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid provider. Must be one of: {sorted(valid)}")
    if body.provider:
        config.llm_provider = body.provider
        _save_settings(config, {"llm_provider": body.provider})
    if body.model_name:
        _set_model_name(config, body.model_name)
        _save_settings(config, {f"{config.llm_provider}_model_name": body.model_name})
    if body.api_key:
        cred_key = _provider_key_map.get(config.llm_provider)
        if cred_key:
            credentials.set(cred_key, body.api_key)
    return {"data": {"provider": config.llm_provider, "model_name": _model_name_for(config)}}


@router.post("/llm/test")
async def test_llm(config: AppConfig = Depends(get_config)):
    from app.services import llm
    from app.core.errors import StageError
    try:
        response = await llm.complete("Say OK in one word.", config)
        return {"data": {"connected": True, "response": response[:100]}}
    except StageError as e:
        return {"data": {"connected": False, "error": str(e)}}
    except Exception as e:
        return {"data": {"connected": False, "error": str(e)}}


def _model_name_for(config: AppConfig) -> str:
    return {
        "ollama": config.ollama_model_name,
        "openai": config.openai_model_name,
        "anthropic": config.anthropic_model_name,
        "gemini": config.gemini_model_name,
    }.get(config.llm_provider, "")


def _set_model_name(config: AppConfig, name: str) -> None:
    p = config.llm_provider
    if p == "ollama":
        config.ollama_model_name = name
    elif p == "openai":
        config.openai_model_name = name
    elif p == "anthropic":
        config.anthropic_model_name = name
    elif p == "gemini":
        config.gemini_model_name = name


# ---------------------------------------------------------------------------
# Schedule settings (Story 8.7)
# ---------------------------------------------------------------------------

class ScheduleBody(BaseModel):
    cadence: str
    time: str = "07:00"
    day_of_week: str = "mon"
    daemon_mode: bool = False


def _next_run(cadence: str, time_str: str) -> str | None:
    if cadence == "off":
        return None
    now = datetime.now()
    h, m = (int(x) for x in time_str.split(":"))
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    if cadence == "every_other_day":
        target += timedelta(days=1)
    elif cadence == "weekly":
        target += timedelta(days=6)
    return target.isoformat()


@router.get("/tts")
async def get_tts_settings(config: AppConfig = Depends(get_config)):
    from app.services.tts import cuda_available
    return {"data": {
        "engine": config.tts_engine,
        "cuda_available": cuda_available(),
        "available_engines": ["kokoro", "orpheus"],
    }}


@router.put("/tts")
async def update_tts(
    engine: str = Form("kokoro"),
    tts_voice: str = Form("af_heart"),
    config: AppConfig = Depends(get_config),
):
    from app.services.tts import VOICES
    valid_engines = {"kokoro", "orpheus"}
    if engine not in valid_engines:
        raise HTTPException(status_code=400, detail=f"Invalid engine. Must be one of: {sorted(valid_engines)}")
    if engine == "orpheus":
        from app.services.tts import cuda_available
        if not cuda_available():
            raise HTTPException(status_code=400, detail="Orpheus requires a CUDA-compatible GPU")
    if tts_voice not in VOICES:
        tts_voice = "af_heart"
    config.tts_engine = engine
    _save_settings(config, {"tts_engine": engine, "tts_voice": tts_voice})
    return {"data": {"engine": engine, "tts_voice": tts_voice}}


@router.post("/tts/test")
async def test_tts(config: AppConfig = Depends(get_config)):
    import tempfile
    from pathlib import Path as _Path
    from fastapi.responses import FileResponse
    from app.core.errors import StageError
    from app.services import tts

    sample = "Welcome to your morning briefing."
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        out_path = _Path(f.name)
    try:
        await tts.synthesize(sample, out_path)
        return FileResponse(str(out_path), media_type="audio/mpeg", filename="sample.mp3")
    except StageError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_setup_status(config: AppConfig = Depends(get_config)):
    import os
    from pathlib import Path as _Path

    # Gmail
    token = credentials.get(credentials.GMAIL_OAUTH_TOKEN)
    gmail_status = "authorized" if token else "not_authorized"

    # Kokoro — check HF cache
    hf_home = os.environ.get("HF_HOME", str(_Path.home() / ".cache" / "huggingface"))
    kokoro_cache = _Path(hf_home) / "hub" / "models--hexgrad--Kokoro-82M"
    kokoro_status = "downloaded" if kokoro_cache.exists() else "not_downloaded"

    # Sections (excluding "Other")
    non_other_sections = [s for s in config.sections if s != "Other"]

    # Schedule
    stored = _load_settings(config)
    cadence = stored.get("cadence", "off")
    time_val = stored.get("schedule_time", "07:00")
    schedule_display = f"{cadence.replace('_', ' ').title()} at {time_val}" if cadence != "off" else "Off"

    return {"data": {
        "gmail": {"status": gmail_status},
        "kokoro": {"status": kokoro_status},
        "sections": {"count": len(non_other_sections), "sections": non_other_sections},
        "llm": {"provider": config.llm_provider},
        "schedule": {"cadence": cadence, "time": time_val, "display": schedule_display},
    }}


@router.get("/schedule")
async def get_schedule(config: AppConfig = Depends(get_config)):
    from app.core import scheduler as sched_mod

    stored = _load_settings(config)
    cadence = stored.get("cadence", "off")
    time_val = stored.get("schedule_time", "07:00")
    daemon_mode = stored.get("daemon_mode", False)
    return {"data": {
        "cadence": cadence,
        "time": time_val,
        "next_run": _next_run(cadence, time_val),
        "daemon_mode": daemon_mode,
        "daemon_alive": sched_mod.check_daemon_alive(config),
    }}


@router.put("/schedule")
async def update_schedule(
    cadence: str = Form("off"),
    time: str = Form("07:00"),
    day_of_week: str = Form("mon"),
    daemon_mode: str | None = Form(None),  # checkbox: present=on, absent=None
    config: AppConfig = Depends(get_config),
):
    from app.core import scheduler as sched_mod

    daemon_mode_bool = daemon_mode is not None
    valid = {"off", "daily", "every_other_day", "weekly"}
    if cadence not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid cadence. Must be one of: {sorted(valid)}")
    _save_settings(config, {
        "cadence": cadence,
        "schedule_time": time,
        "day_of_week": day_of_week,
        "daemon_mode": daemon_mode_bool,
    })

    # Update in-process scheduler immediately
    if sched_mod.scheduler.running:
        sched_mod.schedule_run(cadence, time, config, day_of_week=day_of_week)

    # Start or stop daemon if requested
    if daemon_mode_bool:
        if not sched_mod.check_daemon_alive(config):
            sched_mod.start_daemon(config)
    else:
        sched_mod.stop_daemon(config)

    return {"data": {
        "cadence": cadence,
        "time": time,
        "next_run": _next_run(cadence, time),
        "daemon_mode": daemon_mode_bool,
        "daemon_alive": sched_mod.check_daemon_alive(config),
    }}
