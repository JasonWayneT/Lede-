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


# ---------------------------------------------------------------------------
# synthesize_plan — CR-005 / FR-030
# ---------------------------------------------------------------------------


def _segments():
    return [
        {"role": "intro", "text": "", "selected_music": None, "duration_seconds": None},
        {"role": "main_summary", "text": "Story one.", "selected_music": None, "duration_seconds": None},
        {"role": "main_summary", "text": "Story two.", "selected_music": None, "duration_seconds": None},
        {"role": "outro", "text": "", "selected_music": None, "duration_seconds": None},
    ]


@pytest.mark.asyncio
async def test_synthesize_plan_records_durations_and_writes_one_file(tmp_path):
    # AC-078 — each narrated segment gets a duration; one mp3 is written; structural stay None.
    segments = _segments()

    def fake_render(script):
        return np.zeros(tts.SAMPLE_RATE)  # exactly 1 second of samples

    with patch("app.services.tts._render_samples_sync", side_effect=fake_render), \
         patch("soundfile.write") as mock_write:
        await tts.synthesize_plan(segments, tmp_path / "out.mp3")

    assert segments[1]["duration_seconds"] == 1.0
    assert segments[2]["duration_seconds"] == 1.0
    assert segments[0]["duration_seconds"] is None  # structural segment not rendered
    assert segments[3]["duration_seconds"] is None
    mock_write.assert_called_once()


@pytest.mark.asyncio
async def test_synthesize_plan_no_narrated_segments_raises(tmp_path):
    segments = [{"role": "intro", "text": "", "selected_music": None, "duration_seconds": None}]
    with pytest.raises(StageError):
        await tts.synthesize_plan(segments, tmp_path / "out.mp3")


@pytest.mark.asyncio
async def test_synthesize_plan_applies_pronunciation(tmp_path):
    captured = []

    def fake_render(script):
        captured.append(script)
        return np.zeros(100)

    segments = [{"role": "main_summary", "text": "Hello FAISS.", "selected_music": None, "duration_seconds": None}]
    with patch("app.services.tts._render_samples_sync", side_effect=fake_render), \
         patch("soundfile.write"):
        await tts.synthesize_plan(segments, tmp_path / "out.mp3", pronunciation_guide={"FAISS": "fais"})

    assert "fais" in captured[0]
    assert "FAISS" not in captured[0]
