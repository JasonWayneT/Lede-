"""Briefing file download routes."""

# Implements FR-007, ARCH-001

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import select

from app.db.database import get_session
from app.db.models import BriefingOutput, Run

router = APIRouter(tags=["downloads"])


@router.get("/briefings/{run_id}/download/markdown")
async def download_markdown(run_id: int):
    async with get_session() as session:
        result = await session.execute(
            select(BriefingOutput, Run)
            .join(Run, Run.id == BriefingOutput.run_id)
            .where(BriefingOutput.run_id == run_id)
        )
        row = result.first()

    if not row:
        return JSONResponse(status_code=404, content={"error": "Briefing not found", "code": "NOT_FOUND"})

    output, run = row
    if not output.markdown_path:
        return JSONResponse(status_code=404, content={"error": "Markdown not available", "code": "NOT_FOUND"})

    import os
    if not os.path.exists(output.markdown_path):
        return JSONResponse(status_code=404, content={"error": "File not found on disk", "code": "NOT_FOUND"})

    date_str = run.created_at.strftime("%Y-%m-%d") if run.created_at else str(run_id)
    return FileResponse(
        path=output.markdown_path,
        filename=f"briefing-{date_str}.md",
        media_type="text/markdown",
    )


@router.get("/briefings/{run_id}/download/audio")
async def download_audio(run_id: int):
    async with get_session() as session:
        result = await session.execute(
            select(BriefingOutput, Run)
            .join(Run, Run.id == BriefingOutput.run_id)
            .where(BriefingOutput.run_id == run_id)
        )
        row = result.first()

    if not row:
        return JSONResponse(status_code=404, content={"error": "Briefing not found", "code": "NOT_FOUND"})

    output, run = row
    if not output.audio_path:
        return JSONResponse(status_code=404, content={"error": "Audio not available for this run", "code": "NOT_FOUND"})

    import os
    if not os.path.exists(output.audio_path):
        return JSONResponse(status_code=404, content={"error": "File not found on disk", "code": "NOT_FOUND"})

    date_str = run.created_at.strftime("%Y-%m-%d") if run.created_at else str(run_id)
    return FileResponse(
        path=output.audio_path,
        filename=f"briefing-{date_str}.mp3",
        media_type="audio/mpeg",
    )
