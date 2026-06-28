# Story 7.2: SSE Live Log Queue Integration

Status: ready-for-dev

## Story

As a developer,
I want a shared async queue that the orchestrator writes log events to and the SSE endpoint reads from,
so that the browser receives real-time pipeline progress without polling.

## Acceptance Criteria

1. **Given** a Run starting, **When** the orchestrator begins, **Then** a new `asyncio.Queue` is created in the SSE queue registry keyed by `run_id` (`dict[int, asyncio.Queue]` singleton in `api/stream.py`)

2. **Given** each pipeline stage starting or completing, **When** the orchestrator emits a log event, **Then** a JSON object is placed on the queue: `{"event": "log", "data": {"level": "info", "stage": "embed", "message": "...", "ts": "ISO8601"}}`

3. **Given** a Run completing, **When** the orchestrator emits the final event, **Then** `{"event": "complete", "data": {"run_id": N, "audio_path": "...", "markdown_path": "..."}}` is placed on the queue

4. **Given** a Run entering Hold state, **When** the orchestrator emits the error event, **Then** `{"event": "error", "data": {"code": "STAGE_FAILED", "stage": "...", "message": "...", "retryable": false}}` is placed on the queue

5. **Given** the SSE endpoint at `/api/stream/{run_id}`, **When** a browser connects, **Then** it reads from the queue for that `run_id` and streams events as `text/event-stream` until the queue signals completion

6. **Given** the SSE client disconnecting, **When** the connection closes, **Then** the queue entry for that `run_id` is cleaned up — no memory leak

## Tasks / Subtasks

- [ ] Implement queue registry in `app/api/stream.py` (AC: 1, 5, 6)
  - [ ] `_queues: dict[int, asyncio.Queue] = {}` — module-level singleton
  - [ ] `def get_or_create_queue(run_id: int) -> asyncio.Queue`: create if not exists, return
  - [ ] `def remove_queue(run_id: int) -> None`: delete from dict if present
  - [ ] SSE endpoint: `GET /api/stream/{run_id}` using `sse_starlette.sse.EventSourceResponse`
  - [ ] Generator: `async for event in _read_queue(run_id)` — yield events as SSE until sentinel `None` received
  - [ ] On client disconnect: call `remove_queue(run_id)` in finally block

- [ ] Implement emit helper in `app/pipeline/orchestrator.py` (AC: 2–4)
  - [ ] `def _emit(run_id: int, event: str, data: dict) -> None`: `get_or_create_queue(run_id).put_nowait({"event": event, "data": data})`
  - [ ] `ts` field: `datetime.utcnow().isoformat() + "Z"` for all log events
  - [ ] Sentinel: after complete or error event, put `None` on queue to signal end of stream

- [ ] Register `stream` router in `app/main.py` (AC: 5)
  - [ ] `app.include_router(stream.router, prefix="/api")`

- [ ] Install `sse-starlette` (already in `uv add` from Story 1.1) (AC: 5)
  - [ ] Confirm `from sse_starlette.sse import EventSourceResponse` import works

- [ ] Write tests in `tests/api/test_stream.py` (AC: 1, 2, 5, 6)
  - [ ] Test queue created on `get_or_create_queue()`
  - [ ] Test SSE endpoint streams events from queue
  - [ ] Test queue removed after client disconnect
  - [ ] Test `None` sentinel closes the stream

## Dev Notes

### SSE event format (text/event-stream)

The `EventSourceResponse` from `sse-starlette` handles SSE framing. Each yielded item should be `{"data": json.dumps(payload), "event": event_type}`.

### Queue as module-level singleton

`_queues` is a module-level dict in `api/stream.py`. The orchestrator imports `from app.api import stream` and calls `stream.get_or_create_queue(run_id)`. This is the only cross-boundary import between `api/` and `pipeline/` that is intentional and documented in the architecture gap analysis.

Note: architecture says `main.py` imports `api/`; orchestrator imports `api/stream.py` for queue access. This is acceptable — it is not the same as stages importing from `api/`.

### Memory leak prevention (AC: 6)

If a client connects but the pipeline never starts (race condition), the queue may never receive a sentinel. Add a timeout to `_read_queue`: if no event received for 5 minutes, clean up and close.

### SSE event type vs data field

Each SSE message has:
- `event:` line (e.g. `log`, `complete`, `error`, `status`)
- `data:` line (JSON string of the data payload)

The browser `EventSource` API uses `event.type` to route to the right listener.

### References

- [Source: docs/ARCHITECTURE.md § "Gap Analysis — SSE queue pattern"] — `dict[int, asyncio.Queue]` singleton in `api/stream.py`
- [Source: docs/ARCHITECTURE.md § "Format Patterns — SSE Event Payload"] — exact event shapes
- [Source: docs/epics-stories.md § "Story 7.2"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
