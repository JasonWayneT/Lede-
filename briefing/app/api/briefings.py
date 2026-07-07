"""Briefing trigger, history, and retry routes."""

# Implements FR-003, ARCH-001

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.core.config import AppConfig
from app.db.database import get_session
from app.db.models import BriefingOutput, Run
from app.pipeline import handoff, orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["briefings"])


def get_config() -> AppConfig:
    return AppConfig()


class RunRequest(BaseModel):
    depth: str = "standard"


@router.post("/briefings")
async def start_briefing(
    background_tasks: BackgroundTasks,
    body: RunRequest = RunRequest(),
    config: AppConfig = Depends(get_config),
):
    # BUG-015 (CR-013): the active-run check and the new Run insert used to happen in two
    # separate transactions, leaving a check-then-act race window; the check also only looked
    # for "running", missing the "pending" window before the background task flips status.
    # Doing both in one transaction lets SQLite's single-writer serialization close the race.
    async with get_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Run).where(Run.status.in_(["running", "pending"]))
            )
            active = result.scalars().first()
            if active:
                raise HTTPException(status_code=409, detail="A run is already in progress")

            run = Run(
                status="pending",
                depth=body.depth or config.briefing_depth,
                section_config={"sections": config.sections},
            )
            session.add(run)
        await session.refresh(run)
        run_id = run.id

    background_tasks.add_task(orchestrator.run_pipeline, run_id, config)
    return {"run_id": run_id, "status": "pending"}


@router.get("/briefings")
async def list_briefings():
    async with get_session() as session:
        result = await session.execute(
            select(Run, BriefingOutput)
            .outerjoin(BriefingOutput, BriefingOutput.run_id == Run.id)
            .order_by(Run.created_at.desc(), Run.id.desc())
        )
        rows = result.all()

    data = []
    for run, output in rows:
        section_config = run.section_config or {}
        data.append({
            "run_id": run.id,
            "date": run.created_at.isoformat() if run.created_at else None,
            "status": run.status,
            "error": run.error,
            "section_breakdown": section_config.get("section_breakdown", {}),
            "story_count": section_config.get("story_count", 0),
            "markdown_path": output.markdown_path if output else None,
            "audio_path": output.audio_path if output else None,
        })
    return {"data": data}


@router.post("/briefings/{run_id}/retry")
async def retry_run(
    run_id: int,
    background_tasks: BackgroundTasks,
    config: AppConfig = Depends(get_config),
):
    async with get_session() as session:
        run = await session.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        if run.status != "hold":
            raise HTTPException(status_code=409, detail="Run is not in hold state")

        failed_stage_name = None
        if run.error:
            import re
            m = re.match(r"\[(\w+)\]", run.error)
            if m:
                failed_stage_name = m.group(1)

    artifacts_dir = Path(config.data_dir) / "artifacts"
    stage_nums = {name: num for num, name, _ in orchestrator.STAGES}
    failed_num = stage_nums.get(failed_stage_name, 1)

    last_artifact = None
    for num in range(failed_num - 1, 0, -1):
        candidates = list(artifacts_dir.glob(f"{run_id}/stage_{num:02d}_*.json"))
        if candidates:
            last_artifact = candidates[0]
            break

    if last_artifact:
        packet = handoff.read_packet(last_artifact)
    else:
        from app.pipeline.handoff import HandoffPacket
        packet = HandoffPacket(run_id=run_id)

    async with get_session() as session:
        async with session.begin():
            run = await session.get(Run, run_id)
            run.status = "running"
            run.error = None
            session.add(run)

    async def _resume():
        from app.db.database import get_session as _gs
        from app.db.models import BriefingOutput as _BO, ProcessedEmail as _PE
        from app.api import stream as sse
        from app.core.errors import StageError
        from app.services import tts
        from pathlib import Path as _P

        resume_stages = [(n, nm, m) for n, nm, m in orchestrator.STAGES if n >= failed_num]
        audio_path = None

        async with _gs() as session:
            orchestrator._emit(run_id, "status", {"run_id": run_id, "status": "running", "ts": orchestrator._ts()})
            try:
                packet_result = packet
                for stage_num, stage_name, stage_module in resume_stages:
                    orchestrator._emit(run_id, "status", {"run_id": run_id, "current_stage": stage_name, "ts": orchestrator._ts()})
                    try:
                        packet_result = await stage_module.run(packet_result, config)
                    except StageError as e:
                        packet_result = await orchestrator._retry(stage_module, stage_num, stage_name, packet_result, config, e, session)
                    handoff.write_packet(packet_result, _P(config.data_dir) / "artifacts", stage_num, stage_name)

                # Synthesize audio once after the resume completes — covers both
                # "resuming before assemble" (assemble runs in the loop above)
                # and "resuming after assemble" (e.g. a qa_gate-only retry),
                # where assemble already ran in the original attempt and would
                # otherwise never re-fire, silently skipping audio.
                tts_out = _P(config.data_dir) / "briefings" / str(run_id) / "briefing.mp3"
                if packet_result.tts_script and not tts_out.exists():
                    try:
                        # FR-030 — prefer the segment plan; fall back to the flat script
                        if packet_result.audio_segments:
                            await tts.synthesize_plan(packet_result.audio_segments, tts_out, pronunciation_guide=packet_result.pronunciation_guide)
                        else:
                            await tts.synthesize(packet_result.tts_script, tts_out, pronunciation_guide=packet_result.pronunciation_guide)
                        audio_path = str(tts_out)
                    except StageError:
                        pass
                elif tts_out.exists():
                    audio_path = str(tts_out)

                async with session.begin():
                    run = await session.get(Run, run_id)
                    run.status = "complete"
                    run.error = None
                    session.add(run)
                    session.add(_BO(run_id=run_id, markdown_path=packet_result.markdown_path, audio_path=audio_path))

                    # BUG-018 (CR-013): this resume path never recorded ProcessedEmail rows,
                    # unlike run_pipeline's finalize block -- a successfully retried run would
                    # let Gmail re-fetch and reprocess the same emails on the next run, silently
                    # breaking FR-003's no-duplicate-processing guarantee.
                    email_ids = [
                        getattr(e, "email_id", None) or e.get("email_id", "") if isinstance(e, dict) else getattr(e, "email_id", "")
                        for e in packet_result.emails
                    ]
                    email_ids = [e for e in email_ids if e]
                    already_processed: set[str] = set()
                    if email_ids:
                        from sqlalchemy import select as _select
                        existing = await session.execute(
                            _select(_PE.email_id).where(_PE.email_id.in_(email_ids))
                        )
                        already_processed = {row[0] for row in existing.all()}
                    for email_id in email_ids:
                        if email_id not in already_processed:
                            session.add(_PE(email_id=email_id, run_id=run_id))

                orchestrator._emit(run_id, "complete", {"run_id": run_id, "markdown_path": packet_result.markdown_path, "audio_path": audio_path, "ts": orchestrator._ts()})
            except orchestrator._HoldException:
                pass
            finally:
                orchestrator._emit(run_id, None, None)

    background_tasks.add_task(_resume)
    return {"run_id": run_id, "status": "running"}


@router.delete("/briefings/{run_id}/error")
async def dismiss_error(
    run_id: int,
):
    async with get_session() as session:
        async with session.begin():
            run = await session.get(Run, run_id)
            if not run:
                raise HTTPException(status_code=404, detail="Run not found")
            if run.status != "hold":
                raise HTTPException(status_code=409, detail="Run is not in hold state")
            
            run.status = "failed"
            session.add(run)
    return HTMLResponse(content="")

_MAX_ON_DEMAND_URLS = 10  # BUG-017 (CR-013): cap prevents an unbounded, sequential, per-URL-timeout request


class OnDemandRequest(BaseModel):
    urls: list[str]
    source_type: str = "article"  # "youtube" | "article"


@router.post("/briefings/on-demand")
async def start_on_demand(
    body: OnDemandRequest,
    background_tasks: BackgroundTasks,
    config: AppConfig = Depends(get_config),
):
    """Trigger an on-demand briefing from YouTube or article URLs (FR-26/FR-27)."""
    if not body.urls:
        raise HTTPException(status_code=422, detail="At least one URL is required")
    if len(body.urls) > _MAX_ON_DEMAND_URLS:
        raise HTTPException(
            status_code=422,
            detail=f"Too many URLs — at most {_MAX_ON_DEMAND_URLS} per on-demand request",
        )
    if body.source_type not in ("youtube", "article"):
        raise HTTPException(status_code=422, detail="source_type must be 'youtube' or 'article'")

    # BUG-015 (CR-013): an early check here is just an optimization to skip wasted extraction
    # work -- the check that actually prevents a double-start is the one re-run inside the same
    # transaction as the insert, below, right before extraction time would otherwise leave a race
    # window open. Checking "pending" as well as "running" closes the window before the
    # background task flips a just-created run's status.
    async with get_session() as session:
        result = await session.execute(select(Run).where(Run.status.in_(["running", "pending"])))
        if result.scalars().first():
            raise HTTPException(status_code=409, detail="A run is already in progress")

    # Extract content synchronously before starting the pipeline
    if body.source_type == "youtube":
        from app.services.youtube import fetch_transcripts
        extracted = await fetch_transcripts(body.urls)
    else:
        from app.services.article import fetch_articles
        extracted = await fetch_articles(body.urls)

    if not extracted:
        raise HTTPException(status_code=422, detail="No usable content could be extracted from the provided URLs")

    async with get_session() as session:
        async with session.begin():
            result = await session.execute(select(Run).where(Run.status.in_(["running", "pending"])))
            if result.scalars().first():
                raise HTTPException(status_code=409, detail="A run is already in progress")

            run = Run(
                status="pending",
                depth=config.briefing_depth,
                section_config={
                    "sections": config.sections,
                    "source_type": body.source_type,
                    "source_urls": body.urls,
                },
            )
            session.add(run)
        await session.refresh(run)
        run_id = run.id

    background_tasks.add_task(
        orchestrator.run_pipeline_on_demand,
        run_id,
        extracted,
        config,
        body.source_type,
    )
    return {"run_id": run_id, "status": "pending", "source_count": len(extracted)}


@router.get("/briefings/missed")
async def missed_briefing(config: AppConfig = Depends(get_config)):
    """Report a missed scheduled run so the dashboard can show a banner (FR-026/9-3, BUG-011).

    Derived live from the same check used to trigger the startup retry (`check_missed_runs`),
    rather than cached process state -- this stays correct whether the retry was triggered by the
    web server's own lifespan startup or by the separate daemon subprocess.
    """
    from app.core.scheduler import check_missed_runs

    missed_at = await check_missed_runs(config)
    if not missed_at:
        return {"missed_at": None, "retrying": False}

    async with get_session() as session:
        result = await session.execute(
            select(Run)
            .where(Run.status.in_(["running", "pending"]))
            .order_by(Run.created_at.desc())
            .limit(1)
        )
        active_run = result.scalar_one_or_none()

    return {"missed_at": missed_at.isoformat(), "retrying": active_run is not None}
