"""SSE live log queue registry and streaming endpoint."""

# Implements FR-011, ARCH-004

from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

logger = logging.getLogger(__name__)

router = APIRouter()

_queues: dict[int, asyncio.Queue] = {}

_TIMEOUT_SECONDS = 300


def get_or_create_queue(run_id: int) -> asyncio.Queue:
    if run_id not in _queues:
        _queues[run_id] = asyncio.Queue()
    return _queues[run_id]


def remove_queue(run_id: int) -> None:
    _queues.pop(run_id, None)


async def _read_queue(run_id: int) -> AsyncIterator[dict]:
    queue = get_or_create_queue(run_id)
    try:
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                logger.warning("SSE queue %d timed out — closing stream", run_id)
                break
            if item is None:
                break
            yield {"event": item.get("event", "log"), "data": json.dumps(item.get("data", {}))}
    finally:
        remove_queue(run_id)


@router.get("/stream/{run_id}")
async def stream_run(run_id: int):
    return EventSourceResponse(_read_queue(run_id))
