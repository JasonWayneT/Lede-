"""Tests for app.services.youtube — FR-26."""

import pytest


# ── _extract_video_id ──────────────────────────────────────────────────────

def test_extract_video_id_watch_url():
    from app.services.youtube import _extract_video_id
    vid = _extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert vid == "dQw4w9WgXcQ"


def test_extract_video_id_short_url():
    from app.services.youtube import _extract_video_id
    vid = _extract_video_id("https://youtu.be/dQw4w9WgXcQ")
    assert vid == "dQw4w9WgXcQ"


def test_extract_video_id_shorts_url():
    from app.services.youtube import _extract_video_id
    vid = _extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ")
    assert vid == "dQw4w9WgXcQ"


def test_extract_video_id_invalid_url():
    from app.services.youtube import _extract_video_id
    assert _extract_video_id("https://example.com") is None
    assert _extract_video_id("not a url") is None
    assert _extract_video_id("") is None


# ── fetch_transcript ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_transcript_invalid_url_returns_none():
    from app.services.youtube import fetch_transcript
    result = await fetch_transcript("https://example.com/not-youtube")
    assert result is None


class _FakeSnippet:
    def __init__(self, text):
        self.text = text

class _FakeTranscript:
    def __init__(self, entries):
        self._entries = entries
    def __iter__(self):
        return iter(self._entries)


@pytest.mark.asyncio
async def test_fetch_transcript_mocked_success(monkeypatch):
    from app.services import youtube as yt_module
    from youtube_transcript_api import YouTubeTranscriptApi

    fake_snippets = [_FakeSnippet("word " * 60)] * 2
    fake_transcript = _FakeTranscript(fake_snippets)

    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", lambda self, video_id: fake_transcript)

    result = await yt_module.fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert result is not None
    assert "word" in result
    assert len(result.split()) >= 100


@pytest.mark.asyncio
async def test_fetch_transcript_too_short_returns_none(monkeypatch):
    from youtube_transcript_api import YouTubeTranscriptApi

    fake_transcript = _FakeTranscript([_FakeSnippet("short")])
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", lambda self, video_id: fake_transcript)

    from app.services.youtube import fetch_transcript
    result = await fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert result is None


@pytest.mark.asyncio
async def test_fetch_transcripts_returns_only_successes(monkeypatch):
    call_count = 0

    async def fake_fetch(url):
        nonlocal call_count
        call_count += 1
        return "transcript text " * 20 if "good" in url else None

    from app.services import youtube as yt_module
    monkeypatch.setattr(yt_module, "fetch_transcript", fake_fetch)

    results = await yt_module.fetch_transcripts(["https://good.com", "https://bad.com"])
    assert len(results) == 1
    assert results[0]["url"] == "https://good.com"
    assert "transcript" in results[0]["text"]
    assert call_count == 2
