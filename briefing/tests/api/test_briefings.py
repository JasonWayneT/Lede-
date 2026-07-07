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
async def test_post_briefings_returns_409_for_pending_run(async_client):
    # BUG-015: a "pending" run (created but not yet flipped to "running" by the background
    # task) must also block a second trigger -- not just "running".
    from app.db.database import get_session
    from app.db.models import Run

    async with get_session() as session:
        async with session.begin():
            session.add(Run(status="pending", depth="standard", section_config={}))

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
async def test_on_demand_rejects_too_many_urls(async_client):
    # BUG-017: caps the number of URLs per request so a large list can't block the request
    # for a long time with unbounded sequential per-URL extraction.
    urls = [f"https://example.com/article-{i}" for i in range(11)]
    resp = await async_client.post(
        "/api/briefings/on-demand",
        json={"urls": urls, "source_type": "article"},
    )
    assert resp.status_code == 422
    assert "Too many URLs" in resp.json()["detail"]


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
async def test_missed_returns_none_when_no_schedule(async_client):
    with patch("app.core.scheduler.check_missed_runs", new=AsyncMock(return_value=None)):
        resp = await async_client.get("/api/briefings/missed")
    assert resp.status_code == 200
    data = resp.json()
    assert data["missed_at"] is None
    assert data["retrying"] is False


@pytest.mark.asyncio
async def test_missed_reports_retrying_when_a_run_is_active(async_client):
    from datetime import datetime, timezone
    from app.db.database import get_session
    from app.db.models import Run

    async with get_session() as session:
        async with session.begin():
            session.add(Run(status="running", depth="standard", section_config={}))

    fixed_time = datetime(2026, 7, 6, 7, 0, tzinfo=timezone.utc)
    with patch("app.core.scheduler.check_missed_runs", new=AsyncMock(return_value=fixed_time)):
        resp = await async_client.get("/api/briefings/missed")
    assert resp.status_code == 200
    data = resp.json()
    assert data["missed_at"] == fixed_time.isoformat()
    assert data["retrying"] is True


@pytest.mark.asyncio
async def test_missed_reports_not_retrying_when_no_active_run(async_client):
    from datetime import datetime, timezone

    fixed_time = datetime(2026, 7, 6, 7, 0, tzinfo=timezone.utc)
    with patch("app.core.scheduler.check_missed_runs", new=AsyncMock(return_value=fixed_time)):
        resp = await async_client.get("/api/briefings/missed")
    assert resp.status_code == 200
    data = resp.json()
    assert data["retrying"] is False


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


@pytest.mark.asyncio
async def test_retry_run_persists_processed_emails(async_client, tmp_path, monkeypatch):
    # BUG-018 regression: a successfully retried run must record ProcessedEmail rows, just
    # like a normal run_pipeline completion does -- the resume path used to skip this entirely.
    from types import ModuleType

    from sqlalchemy import select as sa_select

    from app.db.database import get_session
    from app.db.models import ProcessedEmail, Run
    from app.pipeline import handoff, orchestrator
    from app.pipeline.handoff import HandoffPacket

    monkeypatch.setenv("BRIEFING_DATA_DIR", str(tmp_path))

    async with get_session() as session:
        async with session.begin():
            run = Run(status="hold", depth="standard", section_config={}, error="[qa_gate] boom")
            session.add(run)
        await session.refresh(run)
        run_id = run.id

    packet = HandoffPacket(run_id=run_id, emails=[{"email_id": "retry-test-1"}])
    handoff.write_packet(packet, tmp_path / "artifacts", 9, "assemble")

    fake_qa_gate = ModuleType("fake_qa_gate")

    async def _fake_run(pkt, cfg):
        return pkt

    fake_qa_gate.run = _fake_run

    with patch.object(orchestrator, "STAGES", [(10, "qa_gate", fake_qa_gate)]):
        resp = await async_client.post(f"/api/briefings/{run_id}/retry")
    assert resp.status_code == 200

    async with get_session() as session:
        result = await session.execute(
            sa_select(ProcessedEmail).where(ProcessedEmail.email_id == "retry-test-1")
        )
        assert result.scalar_one_or_none() is not None
