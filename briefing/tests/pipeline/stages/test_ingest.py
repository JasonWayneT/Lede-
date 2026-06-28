"""Tests for ingest stage — Story 4.2."""

from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import ingest


def _config():
    return AppConfig(llm_provider="ollama")


def _email(email_id="e1"):
    m = MagicMock()
    m.email_id = email_id
    return m


@pytest.mark.asyncio
async def test_ingest_populates_emails():
    emails = [_email("e1"), _email("e2")]
    packet = HandoffPacket(run_id=1)

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("app.pipeline.stages.ingest.get_session", return_value=mock_session), \
         patch("app.pipeline.stages.ingest.gmail.fetch_unprocessed_emails", new=AsyncMock(return_value=emails)):
        result = await ingest.run(packet, _config())

    assert result.emails == emails
    assert result.early_halt is False


@pytest.mark.asyncio
async def test_ingest_empty_sets_early_halt():
    packet = HandoffPacket(run_id=1)

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("app.pipeline.stages.ingest.get_session", return_value=mock_session), \
         patch("app.pipeline.stages.ingest.gmail.fetch_unprocessed_emails", new=AsyncMock(return_value=[])):
        result = await ingest.run(packet, _config())

    assert result.early_halt is True
    assert result.halt_reason == "no_new_emails"


@pytest.mark.asyncio
async def test_ingest_propagates_stage_error():
    packet = HandoffPacket(run_id=1)

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("app.pipeline.stages.ingest.get_session", return_value=mock_session), \
         patch("app.pipeline.stages.ingest.gmail.fetch_unprocessed_emails",
               new=AsyncMock(side_effect=StageError("ingest", "Gmail down", retryable=True))):
        with pytest.raises(StageError) as exc_info:
            await ingest.run(packet, _config())

    assert exc_info.value.retryable is True


def test_stage_signature():
    sig = inspect.signature(ingest.run)
    params = list(sig.parameters)
    assert "packet" in params
    assert "config" in params
