"""Tests for app.services.article — FR-034 (SSRF guard: CR-009/BUG-008)."""

import asyncio

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


# ── SSRF guard (CR-009 / BUG-008) ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_rejects_non_http_scheme():
    from app.services.article import _is_url_safe_to_fetch
    assert await _is_url_safe_to_fetch("file:///etc/passwd") is False
    assert await _is_url_safe_to_fetch("ftp://example.com/x") is False


@pytest.mark.asyncio
async def test_rejects_loopback_ip():
    from app.services.article import _is_url_safe_to_fetch
    assert await _is_url_safe_to_fetch("http://127.0.0.1:8000/admin") is False


@pytest.mark.asyncio
async def test_rejects_localhost_hostname():
    from app.services.article import _is_url_safe_to_fetch
    assert await _is_url_safe_to_fetch("http://localhost/internal") is False


@pytest.mark.asyncio
async def test_rejects_link_local_metadata_ip():
    from app.services.article import _is_url_safe_to_fetch
    assert await _is_url_safe_to_fetch("http://169.254.169.254/latest/meta-data/") is False


@pytest.mark.asyncio
async def test_rejects_private_network_ip():
    from app.services.article import _is_url_safe_to_fetch
    assert await _is_url_safe_to_fetch("http://10.0.0.5/") is False
    assert await _is_url_safe_to_fetch("http://192.168.1.1/") is False


@pytest.mark.asyncio
async def test_allows_public_ip(monkeypatch):
    from app.services import article as art_module
    monkeypatch.setattr(art_module, "_resolve_ips_sync", lambda hostname: ["93.184.216.34"])
    assert await art_module._is_url_safe_to_fetch("https://example.com/article") is True


@pytest.mark.asyncio
async def test_fails_open_when_dns_does_not_resolve(monkeypatch):
    from app.services import article as art_module
    monkeypatch.setattr(art_module, "_resolve_ips_sync", lambda hostname: [])
    assert await art_module._is_url_safe_to_fetch("https://this-does-not-resolve.invalid/") is True


@pytest.mark.asyncio
async def test_fails_open_on_dns_timeout(monkeypatch):
    from app.services import article as art_module

    async def timing_out_wait_for(coro, timeout):
        coro.close()
        raise asyncio.TimeoutError

    monkeypatch.setattr(art_module.asyncio, "wait_for", timing_out_wait_for)
    assert await art_module._is_url_safe_to_fetch("https://example.com/") is True


@pytest.mark.asyncio
async def test_fetch_article_rejects_unsafe_url_before_extraction(monkeypatch):
    from app.services import article as art_module
    called = []
    monkeypatch.setattr(art_module, "_trafilatura_extract", lambda url: called.append(url))
    assert await art_module.fetch_article("http://127.0.0.1/secret") is None
    assert called == []
