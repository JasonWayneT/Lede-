"""YouTube transcript extraction service — FR-033 (PRD FR-26; see CR-008)."""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_VIDEO_ID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|shorts/)|youtu\.be/)([a-zA-Z0-9_-]{11})"
)
_MIN_WORDS = 100


def _extract_video_id(url: str) -> str | None:
    m = _VIDEO_ID_RE.search(url)
    return m.group(1) if m else None


async def fetch_transcript(url: str) -> str | None:
    """Return plain-text transcript for a YouTube URL, or None on failure."""
    from youtube_transcript_api import YouTubeTranscriptApi

    video_id = _extract_video_id(url)
    if not video_id:
        logger.warning("Could not extract video ID from URL: %s", url)
        return None

    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        text = " ".join(snippet.text for snippet in transcript)
        if len(text.split()) < _MIN_WORDS:
            logger.warning("Transcript too short for %s (%d words)", url, len(text.split()))
            return None
        return text
    except Exception as e:
        logger.warning("Transcript fetch failed for %s: %s", url, e)
        return None


async def fetch_transcripts(urls: list[str]) -> list[dict]:
    """Return list of {url, text} dicts for URLs with usable transcripts."""
    results = []
    for url in urls:
        text = await fetch_transcript(url)
        if text:
            results.append({"url": url, "text": text})
        else:
            logger.warning("Skipping YouTube URL (no transcript): %s", url)
    return results
