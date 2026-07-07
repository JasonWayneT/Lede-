# Story 13.1: YouTube Transcript Ingest

Status: implemented (retroactive spec — see `CR-008`)

> **2026-07-06 note:** this spec was written after the code shipped, to close a documentation gap
> found during an audit pass (`AUDIT_LOG.md` finding P3). It describes actual current behavior in
> `app/services/youtube.py`, not a forward-looking design.

## Story

As a user,
I want to paste a YouTube URL and have its transcript used as source material for a briefing,
so that I can get a listenable, synthesized segment about a video without watching it first.

## Acceptance Criteria

1. **Given** a YouTube URL in `youtube.com/watch?v=`, `youtube.com/shorts/`, or `youtu.be/` form, **When** `_extract_video_id` runs, **Then** the 11-character video ID is extracted; any other URL shape returns `None` and is skipped with a `WARNING` log

2. **Given** a valid video ID, **When** `fetch_transcript` runs, **Then** it calls `YouTubeTranscriptApi().fetch(video_id)` and joins all transcript snippets into one plain-text string

3. **Given** a fetched transcript under 100 words, **When** the word count is checked, **Then** the transcript is discarded and `None` is returned with a `WARNING` log — short/placeholder transcripts are not used as source material

4. **Given** any exception during transcript fetch (no captions available, network failure, private/deleted video), **When** it is caught, **Then** `fetch_transcript` returns `None` with a `WARNING` log — it never raises, so one bad URL does not abort the batch

5. **Given** a list of URLs passed to `fetch_transcripts`, **When** it runs, **Then** it returns only `{url, text}` entries for URLs with a usable transcript; URLs that fail are skipped (not included, not erroring the whole call)

## Implementation

- `app/services/youtube.py` — `fetch_transcript(url)`, `fetch_transcripts(urls)`
- Dependency: `youtube_transcript_api`
- Consumed by: `POST /api/briefings/on-demand` (see `13-3-on-demand-ingest-ui-and-api.md`) when `source_type == "youtube"`
- Extracted `{url, text}` entries are injected directly as `extracted_texts` at the `embed` stage — Gmail ingest and HTML extraction are bypassed entirely for on-demand runs

## Tests

- `tests/services/test_youtube.py` — video-ID extraction across all supported URL shapes, transcript fetch success/failure, min-word skip, batch behavior with mixed good/bad URLs

## Known limitations (carried over from audit)

- No rate limiting or per-video timeout beyond what `youtube_transcript_api` does internally — see `AUDIT_LOG.md` S3 for the related on-demand-endpoint URL-count cap fix.
