"""Tests for settings API — Stories 8.4–8.7."""

from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_get_gmail_settings(async_client):
    with patch("app.core.credentials.get", return_value=None):
        resp = await async_client.get("/api/settings/gmail")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "label" in data
    assert data["oauth_status"] == "not_authorized"


@pytest.mark.asyncio
async def test_put_gmail_label(async_client, tmp_path):
    import app.api.settings as s
    cfg = s.get_config()
    with patch.object(s, "_save_settings"):
        resp = await async_client.put("/api/settings/gmail", data={"label": "My Newsletters"})
    assert resp.status_code == 200
    assert resp.json()["data"]["label"] == "My Newsletters"


@pytest.mark.asyncio
async def test_get_sections(async_client):
    resp = await async_client.get("/api/settings/sections")
    assert resp.status_code == 200
    assert "sections" in resp.json()["data"]


@pytest.mark.asyncio
async def test_put_sections_empty_returns_400(async_client):
    resp = await async_client.put("/api/settings/sections", json={"sections": []})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_put_sections_only_other_returns_400(async_client):
    resp = await async_client.put("/api/settings/sections", json={"sections": ["Other"]})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_put_sections_other_auto_appended(async_client):
    import app.api.settings as s
    with patch.object(s, "_save_settings"):
        resp = await async_client.put("/api/settings/sections", json={"sections": ["AI", "Tech"]})
    assert resp.status_code == 200
    assert "Other" in resp.json()["data"]["sections"]


@pytest.mark.asyncio
async def test_get_depth(async_client):
    resp = await async_client.get("/api/settings/depth")
    assert resp.status_code == 200
    assert resp.json()["data"]["briefing_depth"] in ("brief", "standard", "deep")


@pytest.mark.asyncio
async def test_put_depth_invalid(async_client):
    # BUG-009 (CR-010): route takes a Form body (matches settings.html's hx-put form), not JSON.
    resp = await async_client.put("/api/settings/depth", data={"briefing_depth": "ultra"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_put_depth_valid(async_client):
    import app.api.settings as s
    with patch.object(s, "_save_settings"):
        resp = await async_client.put("/api/settings/depth", data={"briefing_depth": "deep"})
    assert resp.status_code == 200
    assert resp.json()["data"]["briefing_depth"] == "deep"


@pytest.mark.asyncio
async def test_put_depth_json_body_rejected(async_client):
    # BUG-009 regression: a JSON body (the old, broken submission shape) must not silently
    # succeed — it should 422 since the route now requires form-encoded fields.
    resp = await async_client.put("/api/settings/depth", json={"briefing_depth": "deep"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_llm_settings(async_client):
    with patch("app.core.credentials.get", return_value=None):
        resp = await async_client.get("/api/settings/llm")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "provider" in data
    assert data["api_key_set"] is False


@pytest.mark.asyncio
async def test_get_llm_masked_key(async_client):
    import app.api.settings as s
    cfg = s.get_config()
    original_provider = cfg.llm_provider
    cfg.llm_provider = "openai"
    try:
        with patch("app.core.credentials.get", return_value="sk-abcdefghij"):
            resp = await async_client.get("/api/settings/llm")
        data = resp.json()["data"]
        assert data["api_key_set"] is True
        assert "..." in data["api_key_masked"]
        assert "abcdefghij" not in data["api_key_masked"]
    finally:
        cfg.llm_provider = original_provider


@pytest.mark.asyncio
async def test_get_schedule(async_client):
    import app.api.settings as s
    with patch.object(s, "_load_settings", return_value={"cadence": "daily", "schedule_time": "07:00"}):
        resp = await async_client.get("/api/settings/schedule")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["cadence"] == "daily"
    assert data["next_run"] is not None


@pytest.mark.asyncio
async def test_put_schedule_invalid_cadence(async_client):
    resp = await async_client.put("/api/settings/schedule", data={"cadence": "hourly", "time": "07:00"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_put_schedule_off_next_run_none(async_client):
    import app.api.settings as s
    with patch.object(s, "_save_settings"):
        resp = await async_client.put("/api/settings/schedule", json={"cadence": "off", "time": "07:00"})
    assert resp.status_code == 200
    assert resp.json()["data"]["next_run"] is None


# ---------------------------------------------------------------------------
# TTS settings (Story 6.3)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_tts_settings(async_client):
    with patch("app.services.tts.cuda_available", return_value=False):
        resp = await async_client.get("/api/settings/tts")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "engine" in data
    assert "cuda_available" in data
    assert "kokoro" in data["available_engines"]


@pytest.mark.asyncio
async def test_put_tts_kokoro_succeeds(async_client):
    import app.api.settings as s
    with patch.object(s, "_save_settings"):
        resp = await async_client.put("/api/settings/tts", data={"engine": "kokoro"})
    assert resp.status_code == 200
    assert resp.json()["data"]["engine"] == "kokoro"


@pytest.mark.asyncio
async def test_put_tts_orpheus_no_cuda_returns_400(async_client):
    with patch("app.services.tts.cuda_available", return_value=False):
        resp = await async_client.put("/api/settings/tts", data={"engine": "orpheus"})
    assert resp.status_code == 400
    assert "CUDA" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_put_tts_invalid_engine_returns_400(async_client):
    resp = await async_client.put("/api/settings/tts", data={"engine": "coqui"})
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# LLM key storage via credentials (Story 12.2)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_put_llm_stores_api_key(async_client):
    # BUG-009 (CR-010): route takes a Form body (matches settings.html's hx-put form), not JSON.
    import app.api.settings as s
    from app.core import credentials

    cfg = s.get_config()
    original = cfg.llm_provider
    cfg.llm_provider = "openai"
    try:
        with (
            patch.object(s, "_save_settings"),
            patch.object(credentials, "set") as mock_set,
        ):
            resp = await async_client.put(
                "/api/settings/llm",
                data={"provider": "openai", "api_key": "sk-testkey123"},
            )
        assert resp.status_code == 200
        mock_set.assert_called_once_with(credentials.OPENAI_KEY, "sk-testkey123")
    finally:
        cfg.llm_provider = original


@pytest.mark.asyncio
async def test_put_llm_invalid_provider_returns_400(async_client):
    resp = await async_client.put("/api/settings/llm", data={"provider": "not-a-provider"})
    assert resp.status_code == 400
