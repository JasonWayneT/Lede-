"""Tests for app.services.article — FR-27."""

import pytest


# ── _trafilatura_extract ───────────────────────────────────────────────────

def test_trafilatura_extract_returns_none_on_error(monkeypatch):
    import trafilatura
    monkeypatch.setattr(trafilatura, "fetch_url", lambda url: None)
    from app.services.article import _trafilatura_extract
    assert _trafilatura_extract("https://example.com") is None


def test_trafilatura_extract_too_short_returns_none(monkeypatch):
    import trafilatura
    monkeypatch.setattr(trafilatura, "fetch_url", lambda url: "<html>hi</html>")
    monkeypatch.setattr(trafilatura, "extract", lambda html: "short text")
    from app.services.article import _trafilatura_extract
    assert _trafilatura_extract("https://example.com") is None


def test_trafilatura_extract_returns_text_when_long_enough(monkeypatch):
    import trafilatura
    long_text = "word " * 250
    monkeypatch.setattr(trafilatura, "fetch_url", lambda url: "<html>...</html>")
    monkeypatch.setattr(trafilatura, "extract", lambda html: long_text)
    from app.services.article import _trafilatura_extract
    result = _trafilatura_extract("https://example.com")
    assert result == long_text


# ── fetch_article ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_article_uses_trafilatura_first(monkeypatch):
    long_text = "word " * 250
    from app.services import article as art_module
    monkeypatch.setattr(art_module, "_trafilatura_extract", lambda url: long_text)
    jina_called = []
    monkeypatch.setattr(art_module, "_jina_extract", lambda url: jina_called.append(url))
    result = await art_module.fetch_article("https://example.com")
    assert result == long_text
    assert not jina_called


@pytest.mark.asyncio
async def test_fetch_article_falls_back_to_jina(monkeypatch):
    long_text = "word " * 250
    from app.services import article as art_module
    monkeypatch.setattr(art_module, "_trafilatura_extract", lambda url: None)

    async def fake_jina(url):
        return long_text

    monkeypatch.setattr(art_module, "_jina_extract", fake_jina)
    result = await art_module.fetch_article("https://example.com")
    assert result == long_text


@pytest.mark.asyncio
async def test_fetch_article_returns_none_when_both_fail(monkeypatch):
    from app.services import article as art_module
    monkeypatch.setattr(art_module, "_trafilatura_extract", lambda url: None)

    async def fake_jina(url):
        return None

    monkeypatch.setattr(art_module, "_jina_extract", fake_jina)
    assert await art_module.fetch_article("https://example.com") is None


@pytest.mark.asyncio
async def test_fetch_articles_skips_failed_urls(monkeypatch):
    from app.services import article as art_module
    long_text = "word " * 250

    async def fake_fetch(url):
        return long_text if "good" in url else None

    monkeypatch.setattr(art_module, "fetch_article", fake_fetch)
    results = await art_module.fetch_articles(["https://good.com/a", "https://bad.com/b"])
    assert len(results) == 1
    assert results[0]["url"] == "https://good.com/a"
