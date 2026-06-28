"""Extract stage — parse HTML emails into clean text entries."""

# Implements FR-002, ARCH-003

from __future__ import annotations

import html
import logging
import re
from html.parser import HTMLParser

from app.core.config import AppConfig
from app.pipeline.handoff import HandoffPacket

logger = logging.getLogger(__name__)

_SKIP_PATTERNS = re.compile(
    r"(unsubscribe|view in browser|manage preferences|email preferences|opt.?out)",
    re.IGNORECASE,
)
_WHITESPACE = re.compile(r"\s{2,}")


class _TextExtractor(HTMLParser):
    """Minimal HTML → plain text extractor using stdlib html.parser."""

    _SKIP_TAGS = {"script", "style", "img", "head", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth = 0
        self.title: str = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in ("p", "br", "div", "h1", "h2", "h3", "h4", "li", "tr"):
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if self._in_title:
            self.title = data.strip()
        self._parts.append(data)

    def get_text(self) -> str:
        raw = "".join(self._parts)
        lines = [html.unescape(ln) for ln in raw.splitlines()]
        filtered = [ln for ln in lines if not _SKIP_PATTERNS.search(ln)]
        cleaned = "\n".join(filtered)
        return _WHITESPACE.sub(" ", cleaned).strip()


def _extract_one(email: object) -> dict | None:
    raw_html = getattr(email, "raw_html", None) or ""
    if not raw_html.strip():
        return None

    parser = _TextExtractor()
    parser.feed(raw_html)
    text = parser.get_text()
    if not text:
        return None

    title = parser.title or getattr(email, "subject", "") or ""

    return {
        "email_id": getattr(email, "email_id", ""),
        "text": text,
        "title": title,
        "sender_name": getattr(email, "sender_name", ""),
        "date": str(getattr(email, "date", "")),
    }


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    results = []
    for email in packet.emails:
        try:
            extracted = _extract_one(email)
            if extracted:
                results.append(extracted)
        except Exception as e:
            logger.warning("Extract skipped email %s: %s", getattr(email, "email_id", "?"), e)

    packet.extracted_texts = results
    logger.info("Extract: %d of %d emails produced text", len(results), len(packet.emails))
    return packet
