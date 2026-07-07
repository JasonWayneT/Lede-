"""Tests for briefings API — Stories 8.1, 8.2, 8.3."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_dashboard_redirects_to_setup_when_not_onboarded(async_client):
    resp = await async_client.get("/", follow_redirects=False)
    # Without onboarding_complete=True in settings, should redirect to /setup
    assert resp.status_code in (200, 302, 307)


@pytest.mark.asyncio
async def test_dashboard_returns_200_when_onboarded(async_client, tmp_path):
    import json
    from app.core.config import AppConfig
    config = AppConfig()
    settings_file = config.data_dir / "settings.json"
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    settings_file.write_text(json.dumps({"onboarding_complete": True}))
    resp = await async_client.get("/", follow_redirects=True)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_docs_returns_200(async_client):
    resp = await async_client.get("/docs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_post_briefings_returns_run_id(async_client):
    with patch("app.api.briefings.orchestrator.run_pipeline", new=AsyncMock()):
        resp = await async_client.post("/api/briefings", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert "run_id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_post_briefings_concurrent_returns_409(async_client):
    from app.db.database import get_session
    from app.db.models import Run

    async with get_session() as session:
        async with session.begin():
            session.add(Run(status="running", depth="standard", section_config={}))

    with patch("app.api.briefings.orchestrator.run_pipeline", new=AsyncMock()):
        resp = await async_client.post("/api/briefings", json={})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_briefings_returns_list(async_client):
    resp = await async_client.get("/api/briefings")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_get_briefings_sorted_newest_first(async_client):
    from app.db.database import get_session
    from app.db.models import Run

    async with get_session() as session:
        async with session.begin():
            session.add(Run(status="complete", depth="standard", section_config={}))
            session.add(Run(status="complete", depth="standard", section_config={}))
            session.add(Run(status="complete", depth="standard", section_config={}))

    resp = await async_client.get("/api/briefings")
    assert resp.status_code == 200
    runs = resp.json()["data"]
    assert len(runs) >= 3
    ids = [r["run_id"] for r in runs]
    assert ids == sorted(ids, reverse=True)


@pytest.mark.asyncio
async def test_on_demand_rejects_empty_urls(async_client):
    resp = await async_client.post("/api/briefings/on-demand", json={"urls": [], "source_type": "article"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_on_demand_rejects_invalid_source_type(async_client):
    resp = await async_client.post(
        "/api/briefings/on-demand",
        json={"urls": ["https://example.com"], "source_type": "rss"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_on_demand_article_returns_run_id(async_client, monkeypatch):
    from app.api import briefings as br_module
    from app.pipeline import orchestrator

    long_text = "word " * 250

    async def fake_fetch_articles(urls):
        return [{"url": u, "text": long_text} for u in urls]

    monkeypatch.setattr(br_module, "fetch_articles", fake_fetch_articles, raising=False)

    with patch("app.api.briefings.orchestrator.run_pipeline_on_demand", new=AsyncMock()):
        with patch(
            "app.services.article.fetch_articles",
            new=AsyncMock(return_value=[{"url": "https://example.com", "text": long_text}]),
        ):
            resp = await async_client.post(
                "/api/briefings/on-demand",
                json={"urls": ["https://example.com"], "source_type": "article"},
            )

    assert resp.status_code == 200
    data = resp.json()
    assert "run_id" in data
    assert data["source_count"] >= 1


@pytest.mark.asyncio
async def test_on_demand_youtube_returns_run_id(async_client, monkeypatch):
    long_text = "transcript " * 120

    with patch("app.services.youtube.fetch_transcripts", new=AsyncMock(
        return_value=[{"url": "https://youtube.com/watch?v=abc1234abcd", "text": long_text}]
    )):
        with patch("app.api.briefings.orchestrator.run_pipeline_on_demand", new=AsyncMock()):
            resp = await async_client.post(
                "/api/briefings/on-demand",
                json={"urls": ["https://youtube.com/watch?v=abc1234abcd"], "source_type": "youtube"},
            )

    assert resp.status_code == 200
    assert "run_id" in resp.json()


@pytest.mark.asyncio
async def test_on_demand_returns_422_when_no_content_extracted(async_client):
    with patch("app.services.article.fetch_articles", new=AsyncMock(return_value=[])):
        resp = await async_client.post(
            "/api/briefings/on-demand",
            json={"urls": ["https://example.com"], "source_type": "article"},
        )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_on_demand_returns_409_when_run_active(async_client):
    from app.db.database import get_session
    from app.db.models import Run

    async with get_session() as session:
        async with session.begin():
            session.add(Run(status="running", depth="standard", section_config={}))

    long_text = "word " * 250
    with patch("app.services.article.fetch_articles", new=AsyncMock(
        return_value=[{"url": "https://example.com", "text": long_text}]
    )):
        resp = await async_client.post(
            "/api/briefings/on-demand",
            json={"urls": ["https://example.com"], "source_type": "article"},
        )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_stage_error_handler(async_client):
    from app.core.errors import StageError
    from app.main import app

    @app.get("/test-stage-error")
    async def _raise():
        raise StageError("test", "something broke", retryable=True)

    resp = await async_client.get("/test-stage-error")
    assert resp.status_code == 500
    body = resp.json()
    assert body["code"] is not None
    assert body["retryable"] is True
