# Story 13.2: Article URL Ingest

Status: implemented (retroactive spec — see `CR-008`); SSRF hardening tracked separately under `CR-009`/`BUG-008`

> **2026-07-06 note:** this spec was written after the code shipped, to close a documentation gap
> found during an audit pass (`AUDIT_LOG.md` finding P3). It describes actual current behavior in
> `app/services/article.py`. A real security gap was found alongside it (no protection against the
> service being used to reach internal/private network addresses) — see `CR-009`/`BUG-008` for the
> fix; this spec should be re-read together with that CR.

## Story

As a user,
I want to paste an article URL and have its body text used as source material for a briefing,
so that I can get a synthesized, listenable segment about an article without reading it first.

## Acceptance Criteria

1. **Given** an article URL, **When** `fetch_article` runs, **Then** it first attempts extraction via `trafilatura.fetch_url` + `trafilatura.extract`

2. **Given** a `trafilatura` extraction result under 200 words (or no result at all), **When** the word count is checked, **Then** the system falls back to Jina Reader (`https://r.jina.ai/{url}`, 30s timeout, `Accept: text/plain`)

3. **Given** the Jina Reader fallback also returns under 200 words, or the request fails, **When** the failure is caught, **Then** `fetch_article` returns `None` — the URL is skipped, not retried, not erroring the batch

4. **Given** any exception in either extractor (network failure, malformed HTML, non-2xx response), **When** it is caught, **Then** it is logged as a `WARNING` and treated as extraction failure for that URL, never raised to the caller

5. **Given** a list of URLs passed to `fetch_articles`, **When** it runs, **Then** it returns only `{url, text}` entries for URLs with usable body text; failed URLs are skipped

6. **Given** any URL passed to either extractor, **When** the request is made, **Then** — per `CR-009`/`BUG-008` — the URL's scheme is restricted to `http`/`https` and its resolved host is rejected if it is a loopback, private, link-local, or multicast address, before any network fetch happens

## Implementation

- `app/services/article.py` — `fetch_article(url)`, `fetch_articles(urls)`, `_trafilatura_extract`, `_jina_extract`
- Dependencies: `trafilatura`, `httpx`
- Consumed by: `POST /api/briefings/on-demand` (see `13-3-on-demand-ingest-ui-and-api.md`) when `source_type == "article"`
- Extracted `{url, text}` entries are injected directly as `extracted_texts` at the `embed` stage — Gmail ingest and HTML extraction are bypassed entirely for on-demand runs

## Tests

- `tests/services/test_article.py` — trafilatura success/insufficient-text paths, Jina fallback trigger and success/failure, min-word thresholds
- SSRF guard regression tests added under `CR-009`/`BUG-008`
