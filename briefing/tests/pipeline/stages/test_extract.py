"""Tests for extract stage — Story 4.3."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.core.config import AppConfig
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import extract


def _email(email_id="e1", raw_html="<p>Hello world</p>", subject="Test", sender="Sender", date=None):
    m = MagicMock()
    m.email_id = email_id
    m.raw_html = raw_html
    m.subject = subject
    m.sender_name = sender
    m.date = date or datetime(2024, 1, 1)
    return m


def _config():
    return AppConfig(llm_provider="ollama")


@pytest.mark.asyncio
async def test_extract_clean_html():
    packet = HandoffPacket(run_id=1, emails=[_email(raw_html="<p>Hello world</p>")])
    result = await extract.run(packet, _config())
    assert len(result.extracted_texts) == 1
    assert "Hello world" in result.extracted_texts[0]["text"]


@pytest.mark.asyncio
async def test_extract_strips_unsubscribe():
    html = "<p>Great content here</p><p>Unsubscribe from this list</p>"
    packet = HandoffPacket(run_id=1, emails=[_email(raw_html=html)])
    result = await extract.run(packet, _config())
    text = result.extracted_texts[0]["text"]
    assert "Unsubscribe" not in text
    assert "Great content" in text


@pytest.mark.asyncio
async def test_extract_skips_empty_body(caplog):
    import logging
    packet = HandoffPacket(run_id=1, emails=[_email(raw_html="")])
    with caplog.at_level(logging.WARNING):
        result = await extract.run(packet, _config())
    assert len(result.extracted_texts) == 0


@pytest.mark.asyncio
async def test_extract_result_has_required_fields():
    packet = HandoffPacket(run_id=1, emails=[_email(raw_html="<p>News</p>")])
    result = await extract.run(packet, _config())
    entry = result.extracted_texts[0]
    for key in ("email_id", "text", "title", "sender_name", "date"):
        assert key in entry


@pytest.mark.asyncio
async def test_extract_no_llm_import():
    import app.pipeline.stages.extract as ext_module
    import importlib
    src = importlib.util.find_spec("app.pipeline.stages.extract").origin
    with open(src) as f:
        code = f.read()
    assert "llm" not in code
