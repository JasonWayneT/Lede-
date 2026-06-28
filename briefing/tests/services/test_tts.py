"""Tests for TTS service — Story 6.2."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.core.errors import StageError
from app.services import tts


@pytest.mark.asyncio
async def test_synthesize_writes_file(tmp_path):
    output = tmp_path / "test.mp3"

    def fake_sync(script, out_path):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"fake-audio")

    with patch("app.services.tts._synthesize_sync", side_effect=fake_sync):
        await tts.synthesize("Hello world.", output)

    assert output.exists()


@pytest.mark.asyncio
async def test_synthesize_raises_stage_error_on_failure(tmp_path):
    output = tmp_path / "fail.mp3"

    with patch("app.services.tts._synthesize_sync", side_effect=RuntimeError("OOM")):
        with pytest.raises(StageError) as exc_info:
            await tts.synthesize("Hello.", output)

    assert exc_info.value.retryable is False


@pytest.mark.asyncio
async def test_synthesize_applies_pronunciation_guide(tmp_path):
    output = tmp_path / "test.mp3"
    captured = []

    def fake_sync(script, out_path):
        captured.append(script)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"audio")

    with patch("app.services.tts._synthesize_sync", side_effect=fake_sync):
        await tts.synthesize("Hello FAISS world.", output, pronunciation_guide={"FAISS": "fais"})

    assert "fais" in captured[0]
    assert "FAISS" not in captured[0]
