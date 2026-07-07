"""Article body extraction service — FR-034 (PRD FR-27; see CR-008).

Primary: trafilatura.
Fallback: Jina Reader (r.jina.ai/{url}) when trafilatura returns < 200 words.
SSRF guard: see CR-009/BUG-008 — only http(s) schemes and public hosts are fetched.
"""

from __future__ import annotations

import asyncio
import ipaddress
import logging
import socket
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

_MIN_WORDS = 200
_JINA_TIMEOUT = 30
_ALLOWED_SCHEMES = {"http", "https"}
_DNS_TIMEOUT_SECONDS = 5


def _is_disallowed_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _resolve_ips_sync(hostname: str) -> list[str]:
    try:
        addrinfo = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return []
    return [sockaddr[0] for (*_, sockaddr) in addrinfo]


async def _is_url_safe_to_fetch(url: str) -> bool:
    """SSRF guard (CR-009 / BUG-008).

    Rejects non-http(s) schemes and hosts that resolve to a loopback, private,
    link-local, multicast, or reserved address -- so a user-supplied URL can't
    be used to make this server fetch its own internal network or a cloud
    metadata endpoint. Fails open (returns True) if the hostname simply
    doesn't resolve or DNS times out: that's an ordinary fetch failure the
    extractor will hit on its own, not a security concern.
    """
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    try:
        ips = await asyncio.wait_for(
            asyncio.to_thread(_resolve_ips_sync, hostname), timeout=_DNS_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        return True
    return not any(_is_disallowed_ip(ip) for ip in ips)


async def fetch_article(url: str) -> str | None:
    """Return article body text for a URL, or None if extraction fails."""
    if not await _is_url_safe_to_fetch(url):
        logger.warning("Rejecting unsafe URL for article extraction: %s", url)
        return None

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
