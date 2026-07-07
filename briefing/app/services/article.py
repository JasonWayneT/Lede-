"""Article body extraction service — FR-27.

Primary: trafilatura.
Fallback: Jina Reader (r.jina.ai/{url}) when trafilatura returns < 200 words.
"""

from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)

_MIN_WORDS = 200
_JINA_TIMEOUT = 30


async def fetch_article(url: str) -> str | None:
    """Return article body text for a URL, or None if extraction fails."""
    text = _trafilatura_extract(url)
    if text:
        return text

    logger.info("trafilatura returned insufficient text for %s — trying Jina Reader", url)
    return await _jina_extract(url)


def _trafilatura_extract(url: str) -> str | None:
    import trafilatura

    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        text = trafilatura.extract(downloaded)
        if text and len(text.split()) >= _MIN_WORDS:
            return text
        return None
    except Exception as e:
        logger.warning("trafilatura failed for %s: %s", url, e)
        return None


async def _jina_extract(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=_JINA_TIMEOUT, follow_redirects=True) as client:
            r = await client.get(
                f"https://r.jina.ai/{url}",
                headers={"Accept": "text/plain", "X-Return-Format": "text"},
            )
            r.raise_for_status()
            text = r.text.strip()
            if len(text.split()) >= _MIN_WORDS:
                return text
            logger.warning("Jina Reader returned insufficient text for %s (%d words)", url, len(text.split()))
            return None
    except Exception as e:
        logger.warning("Jina Reader failed for %s: %s", url, e)
        return None


async def fetch_articles(urls: list[str]) -> list[dict]:
    """Return list of {url, text} dicts for URLs with usable article bodies."""
    results = []
    for url in urls:
        text = await fetch_article(url)
        if text:
            results.append({"url": url, "text": text})
        else:
            logger.warning("Skipping article URL (extraction failed): %s", url)
    return results
