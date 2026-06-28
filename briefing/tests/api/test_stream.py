"""Tests for SSE stream module — Story 7.2."""

from __future__ import annotations

import asyncio

import pytest

from app.api import stream as sse


@pytest.fixture(autouse=True)
def _cleanup():
    """Ensure each test gets a clean queue registry."""
    sse._queues.clear()
    yield
    sse._queues.clear()


def test_get_or_create_queue_creates_new():
    q = sse.get_or_create_queue(42)
    assert isinstance(q, asyncio.Queue)
    assert 42 in sse._queues


def test_get_or_create_queue_returns_same():
    q1 = sse.get_or_create_queue(10)
    q2 = sse.get_or_create_queue(10)
    assert q1 is q2


def test_remove_queue():
    sse.get_or_create_queue(7)
    sse.remove_queue(7)
    assert 7 not in sse._queues


def test_remove_queue_missing_is_noop():
    sse.remove_queue(99)  # should not raise


@pytest.mark.asyncio
async def test_sentinel_closes_stream():
    run_id = 1
    q = sse.get_or_create_queue(run_id)
    q.put_nowait({"event": "log", "data": {"message": "hello"}})
    q.put_nowait(None)  # sentinel

    events = []
    async for evt in sse._read_queue(run_id):
        events.append(evt)

    assert len(events) == 1
    assert events[0]["event"] == "log"
    # Queue cleaned up after iteration
    assert run_id not in sse._queues
