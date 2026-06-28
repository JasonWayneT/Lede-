"""Onboarding wizard routes (Epic 10)."""

# Implements FR-014

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core import credentials
from app.core.config import AppConfig

logger = logging.getLogger(__name__)

router = APIRouter(tags=["setup"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


def _config() -> AppConfig:
    return AppConfig()


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


def is_onboarding_complete(config: AppConfig) -> bool:
    stored = _load_settings(config)
    return bool(stored.get("onboarding_complete", False))


@router.get("/setup", response_class=HTMLResponse)
async def setup_entry(request: Request):
    return RedirectResponse("/setup/step/1")


@router.get("/setup/step/1", response_class=HTMLResponse)
async def step1(request: Request):
    config = _config()
    token = credentials.get(credentials.GMAIL_OAUTH_TOKEN)
    authorized_email = None
    if token:
        try:
            authorized_email = json.loads(token).get("email")
        except Exception:
            pass
    return templates.TemplateResponse(request, "setup/step1.html", {
        "oauth_status": "authorized" if token else "not_authorized",
        "authorized_email": authorized_email,
    })


@router.get("/setup/step/2", response_class=HTMLResponse)
async def step2(request: Request):
    return templates.TemplateResponse(request, "setup/step2.html", {})


@router.get("/setup/step/3", response_class=HTMLResponse)
async def step3(request: Request):
    config = _config()
    return templates.TemplateResponse(request, "setup/step3.html", {
        "gmail_label": config.gmail_label,
        "sections": config.sections,
    })


@router.post("/setup/step/3/complete")
async def step3_complete(request: Request):
    from app.api import settings as settings_mod
    config = _config()
    form = await request.form()
    if form.get("gmail_label"):
        config.gmail_label = form["gmail_label"]
        _save_settings(config, {"gmail_label": form["gmail_label"]})
    if form.get("sections"):
        secs = [s.strip() for s in str(form["sections"]).split(",") if s.strip()]
        if "Other" not in secs:
            secs.append("Other")
        _save_settings(config, {"sections": secs})
    return {"status": "ok"}


@router.get("/setup/step/4", response_class=HTMLResponse)
async def step4(request: Request):
    return templates.TemplateResponse(request, "setup/step4.html", {})


@router.post("/setup/step/4/complete")
async def step4_complete(request: Request):
    config = _config()
    form = await request.form()
    cadence = form.get("cadence", "off")
    time_val = form.get("time", "07:00")
    day_of_week = form.get("day_of_week", "mon")
    _save_settings(config, {"cadence": cadence, "schedule_time": time_val, "day_of_week": day_of_week})
    return {"status": "ok"}


@router.get("/setup/complete", response_class=HTMLResponse)
async def setup_complete(request: Request):
    config = _config()
    _save_settings(config, {"onboarding_complete": True})
    return RedirectResponse("/")
