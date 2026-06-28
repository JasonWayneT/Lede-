"""Tests for onboarding wizard and setup status — Stories 10.1, 10.2."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from app.api.setup import is_onboarding_complete
from app.core.config import AppConfig


def _write_settings(config, data):
    path = config.data_dir / "settings.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


@pytest.mark.asyncio
async def test_setup_step1_renders(async_client):
    with patch("app.core.credentials.get", return_value=None):
        resp = await async_client.get("/setup/step/1")
    assert resp.status_code == 200
    assert b"Authorize Gmail" in resp.content


@pytest.mark.asyncio
async def test_setup_step2_renders(async_client):
    resp = await async_client.get("/setup/step/2")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_setup_complete_sets_flag(async_client):
    from app.core.config import AppConfig
    config = AppConfig()
    resp = await async_client.get("/setup/complete", follow_redirects=False)
    assert resp.status_code in (302, 307)
    stored = json.loads((config.data_dir / "settings.json").read_text())
    assert stored.get("onboarding_complete") is True


def test_is_onboarding_complete_false_by_default(tmp_path):
    config = AppConfig.model_validate({"llm_provider": "ollama", "BRIEFING_DATA_DIR": str(tmp_path)})
    # No settings.json → not complete
    assert is_onboarding_complete(config) is False


@pytest.mark.asyncio
async def test_get_settings_status(async_client):
    with patch("app.core.credentials.get", return_value=None):
        resp = await async_client.get("/api/settings/status")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "gmail" in data
    assert "kokoro" in data
    assert "sections" in data
    assert "llm" in data
    assert "schedule" in data


@pytest.mark.asyncio
async def test_get_settings_status_gmail_not_authorized(async_client):
    with patch("app.core.credentials.get", return_value=None):
        resp = await async_client.get("/api/settings/status")
    assert resp.json()["data"]["gmail"]["status"] == "not_authorized"


@pytest.mark.asyncio
async def test_get_settings_status_schedule_off(async_client):
    resp = await async_client.get("/api/settings/status")
    assert resp.json()["data"]["schedule"]["cadence"] == "off"
