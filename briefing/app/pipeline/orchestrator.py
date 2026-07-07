"""Pipeline orchestrator — stage sequencing, retry, DB writes, SSE events."""

# Implements FR-003, ARCH-003

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from types import ModuleType

from sqlalchemy.ext.asyncio import AsyncSession

from app.api import stream as sse
from app.core.config import AppConfig
from app.core.errors import StageError
from app.db.database import get_session
from app.db.models import BriefingOutput, ProcessedEmail, Run
from app.pipeline import handoff
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import (
    assemble,
    cluster,
    draft,
    embed,
    extract,
    frame,
    ingest,
    qa_gate,
    select,
    tts_prep,
)
from app.services import tts

logger = logging.getLogger(__name__)

STAGES: list[tuple[int, str, ModuleType]] = [
    (1, "ingest",    ingest),
    (2, "extract",   extract),
    (3, "embed",     embed),
    (4, "cluster",   cluster),
    (5, "select",    select),
    (6, "frame",     frame),
    (7, "draft",     draft),
    (8, "tts_prep",  tts_prep),
    (9, "assemble",  assemble),
    (10, "qa_gate",  qa_gate),
]


class _HoldException(Exception):
    """Raised when the pipeline enters Hold state — stops further stage execution."""


def _ts() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _emit(run_id: int, event: str, data: dict) -> None:
    q = sse.get_or_create_queue(run_id)
    q.put_nowait({"event": event, "data": data})


async def _retry(
    stage_module: ModuleType,
    stage_num: int,
    stage_name: str,
    packet: HandoffPacket,
    config: AppConfig,
    error: StageError,
    session: AsyncSession,
) -> HandoffPacket:
    _emit(packet.run_id, "error", {
        "code": error.code,
        "stage": stage_name,
        "message": error.message,
        "retryable": error.retryable,
        "ts": _ts(),
    })

    if not error.retryable:
        await _enter_hold(packet.run_id, stage_name, error.message, session)

    # Tier 1
    config._retry_context = {"tier": 1, "error": error.message}
    try:
        logger.info("Retry tier 1: %s", stage_name)
        result = await stage_module.run(packet, config)
        config._retry_context = {}
        return result
    except StageError as e1:
        _emit(packet.run_id, "error", {
            "code": e1.code, "stage": stage_name, "message": e1.message,
            "retryable": e1.retryable, "tier": 1, "ts": _ts(),
        })

        # Tier 2
        config._retry_context = {
            "tier": 2,
            "error": e1.message,
            "guidance": "Attempt with expanded context and explicit correction.",
        }
        try:
            logger.info("Retry tier 2: %s", stage_name)
            result = await stage_module.run(packet, config)
            config._retry_context = {}
            return result
        except StageError as e2:
            _emit(packet.run_id, "error", {
                "code": e2.code, "stage": stage_name, "message": e2.message,
                "retryable": False, "tier": 2, "ts": _ts(),
            })
            config._retry_context = {}
            await _enter_hold(packet.run_id, stage_name, e2.message, session)

    # unreachable — _enter_hold raises _HoldException
    raise _HoldException()


async def _enter_hold(run_id: int, stage_name: str, error_msg: str, session: AsyncSession) -> None:
    async with session.begin():
        run = await session.get(Run, run_id)
        if run:
            run.status = "hold"
            run.error = f"[{stage_name}] {error_msg}"
            session.add(run)
    _emit(run_id, "error", {
        "code": "STAGE_FAILED", "stage": stage_name,
        "message": error_msg, "retryable": False, "ts": _ts(),
    })
    _emit(run_id, None, None)  # sentinel
    raise _HoldException(f"[{stage_name}] {error_msg}")


async def run_pipeline(run_id: int, config: AppConfig) -> None:
    artifacts_dir = Path(config.data_dir) / "artifacts"
    packet = HandoffPacket(run_id=run_id)

    async with get_session() as session:
        # Mark run as running
        async with session.begin():
            run = await session.get(Run, run_id)
            if run:
                run.status = "running"
                session.add(run)

        _emit(run_id, "status", {"run_id": run_id, "status": "running", "ts": _ts()})

        audio_path: str | None = None

        try:
            for stage_num, stage_name, stage_module in STAGES:
                _emit(run_id, "status", {
                    "run_id": run_id, "status": "running",
                    "current_stage": stage_name, "ts": _ts(),
                })

                try:
                    packet = await stage_module.run(packet, config)
                except StageError as e:
                    packet = await _retry(
                        stage_module, stage_num, stage_name, packet, config, e, session
                    )

                # Check early halt after ingest
                if stage_name == "ingest" and packet.early_halt:
                    async with session.begin():
                        run = await session.get(Run, run_id)
                        if run:
                            run.status = "no_new_emails"
                            session.add(run)
                    _emit(run_id, "status", {"run_id": run_id, "status": "no_new_emails", "ts": _ts()})
                    _emit(run_id, None, None)
                    return

                # Write artifact to disk (skip qa_gate here — done after TTS)
                if stage_name != "assemble":
                    handoff.write_packet(packet, artifacts_dir, stage_num, stage_name)
                    _emit(run_id, "log", {
                        "level": "info", "stage": stage_name,
                        "message": f"{stage_name} complete", "ts": _ts(),
                    })

                # After assemble: run TTS (non-fatal) then write assemble artifact
                if stage_name == "assemble":
                    handoff.write_packet(packet, artifacts_dir, stage_num, stage_name)
                    _emit(run_id, "log", {
                        "level": "info", "stage": "assemble",
                        "message": "assemble complete", "ts": _ts(),
                    })
                    tts_output = Path(config.data_dir) / "briefings" / str(run_id) / "briefing.mp3"
                    try:
                        # FR-030 — synthesize from the segment plan; fall back to the flat script
                        if packet.audio_segments:
                            await tts.synthesize_plan(
                                packet.audio_segments,
                                tts_output,
                                pronunciation_guide=packet.pronunciation_guide,
                            )
                        else:
                            await tts.synthesize(
                                packet.tts_script,
                                tts_output,
                                pronunciation_guide=packet.pronunciation_guide,
                            )
                        audio_path = str(tts_output)
                        _emit(run_id, "log", {"level": "info", "stage": "tts", "message": "Audio synthesized", "ts": _ts()})
                    except StageError as tts_err:
                        logger.error("TTS failed (non-fatal): %s", tts_err.message)
                        _emit(run_id, "log", {"level": "warning", "stage": "tts", "message": f"Audio skipped: {tts_err.message}", "ts": _ts()})

            # Tally section breakdown from drafted stories
            section_breakdown: dict[str, int] = {}
            for story in packet.drafted_stories:
                sec = story.get("section_name", "Other") if isinstance(story, dict) else "Other"
                section_breakdown[sec] = section_breakdown.get(sec, 0) + 1
            story_count = sum(section_breakdown.values())

            # Atomic final commit
            async with session.begin():
                run = await session.get(Run, run_id)
                if run:
                    run.status = "complete"
                    run.error = None
                    from sqlalchemy.orm.attributes import flag_modified
                    existing_cfg = dict(run.section_config or {})
                    existing_cfg["story_count"] = story_count
                    existing_cfg["section_breakdown"] = section_breakdown
                    run.section_config = existing_cfg
                    flag_modified(run, "section_config")
                    session.add(run)

                session.add(BriefingOutput(
                    run_id=run_id,
                    markdown_path=packet.markdown_path,
                    audio_path=audio_path,
                ))

                email_ids = [
                    getattr(e, "email_id", None) or e.get("email_id", "") if isinstance(e, dict) else getattr(e, "email_id", "")
                    for e in packet.emails
                ]
                for email_id in email_ids:
                    if email_id:
                        session.add(ProcessedEmail(email_id=email_id, run_id=run_id))

            _emit(run_id, "complete", {
                "run_id": run_id,
                "markdown_path": packet.markdown_path,
                "audio_path": audio_path,
                "ts": _ts(),
            })
            _emit(run_id, None, None)  # sentinel

        except _HoldException:
            pass  # already handled in _enter_hold
        except Exception as e:
            logger.exception("Unexpected orchestrator error for run %d", run_id)
            async with session.begin():
                run = await session.get(Run, run_id)
                if run:
                    run.status = "failed"
                    run.error = str(e)
                    session.add(run)
            _emit(run_id, "error", {"code": "STAGE_FAILED", "message": str(e), "ts": _ts()})
            _emit(run_id, None, None)


ON_DEMAND_STAGES = STAGES[2:]  # embed → qa_gate (skip ingest + extract)


async def run_pipeline_on_demand(
    run_id: int,
    extracted_texts: list[dict],
    config: AppConfig,
    source_type: str = "article",
) -> None:
    """Run pipeline from embed stage with pre-supplied extracted texts.

    Used by the YouTube and Article on-demand ingest modes (FR-26/FR-27).
    Bypasses ingest and extract; injects extracted_texts directly into the
    HandoffPacket before the embed stage runs.
    """
    artifacts_dir = Path(config.data_dir) / "artifacts"
    packet = HandoffPacket(run_id=run_id, extracted_texts=extracted_texts)

    async with get_session() as session:
        async with session.begin():
            run = await session.get(Run, run_id)
            if run:
                run.status = "running"
                session.add(run)

        _emit(run_id, "status", {"run_id": run_id, "status": "running", "ts": _ts()})

        audio_path: str | None = None

        try:
            for stage_num, stage_name, stage_module in ON_DEMAND_STAGES:
                _emit(run_id, "status", {
                    "run_id": run_id, "status": "running",
                    "current_stage": stage_name, "ts": _ts(),
                })

                try:
                    packet = await stage_module.run(packet, config)
                except StageError as e:
                    packet = await _retry(
                        stage_module, stage_num, stage_name, packet, config, e, session
                    )

                if stage_name != "assemble":
                    handoff.write_packet(packet, artifacts_dir, stage_num, stage_name)
                    _emit(run_id, "log", {
                        "level": "info", "stage": stage_name,
                        "message": f"{stage_name} complete", "ts": _ts(),
                    })

                if stage_name == "assemble":
                    handoff.write_packet(packet, artifacts_dir, stage_num, stage_name)
                    _emit(run_id, "log", {
                        "level": "info", "stage": "assemble",
                        "message": "assemble complete", "ts": _ts(),
                    })
                    tts_output = Path(config.data_dir) / "briefings" / str(run_id) / "briefing.mp3"
                    try:
                        # FR-030 — synthesize from the segment plan; fall back to the flat script
                        if packet.audio_segments:
                            await tts.synthesize_plan(
                                packet.audio_segments,
                                tts_output,
                                pronunciation_guide=packet.pronunciation_guide,
                            )
                        else:
                            await tts.synthesize(
                                packet.tts_script,
                                tts_output,
                                pronunciation_guide=packet.pronunciation_guide,
                            )
                        audio_path = str(tts_output)
                        _emit(run_id, "log", {"level": "info", "stage": "tts", "message": "Audio synthesized", "ts": _ts()})
                    except StageError as tts_err:
                        logger.error("TTS failed (non-fatal): %s", tts_err.message)
                        _emit(run_id, "log", {"level": "warning", "stage": "tts", "message": f"Audio skipped: {tts_err.message}", "ts": _ts()})

            section_breakdown: dict[str, int] = {}
            for story in packet.drafted_stories:
                sec = story.get("section_name", "Other") if isinstance(story, dict) else "Other"
                section_breakdown[sec] = section_breakdown.get(sec, 0) + 1
            story_count = sum(section_breakdown.values())

            async with session.begin():
                run = await session.get(Run, run_id)
                if run:
                    run.status = "complete"
                    run.error = None
                    from sqlalchemy.orm.attributes import flag_modified
                    existing_cfg = dict(run.section_config or {})
                    existing_cfg["story_count"] = story_count
                    existing_cfg["section_breakdown"] = section_breakdown
                    existing_cfg["source_type"] = source_type
                    run.section_config = existing_cfg
                    flag_modified(run, "section_config")
                    session.add(run)

                session.add(BriefingOutput(
                    run_id=run_id,
                    markdown_path=packet.markdown_path,
                    audio_path=audio_path,
                ))

            _emit(run_id, "complete", {
                "run_id": run_id,
                "markdown_path": packet.markdown_path,
                "audio_path": audio_path,
                "ts": _ts(),
            })
            _emit(run_id, None, None)

        except _HoldException:
            pass
        except Exception as e:
            logger.exception("Unexpected orchestrator error for on-demand run %d", run_id)
            async with session.begin():
                run = await session.get(Run, run_id)
                if run:
                    run.status = "failed"
                    run.error = str(e)
                    session.add(run)
            _emit(run_id, "error", {"code": "STAGE_FAILED", "message": str(e), "ts": _ts()})
            _emit(run_id, None, None)


async def start_run(config: AppConfig) -> int:
    async with get_session() as session:
        async with session.begin():
            run = Run(
                status="pending",
                depth=config.briefing_depth,
                section_config={"sections": config.sections},
            )
            session.add(run)
        await session.refresh(run)
        return run.id


# ---------------------------------------------------------------------------
# DB helpers (Story 2.3 — kept for backward compatibility)
# ---------------------------------------------------------------------------

async def finalize_run_success(*, session: AsyncSession, run_id: int, email_ids: list[str]) -> None:
    async with session.begin():
        run = await session.get(Run, run_id)
        if run is None:
            raise ValueError(f"Run {run_id} not found")
        run.status = "complete"
        run.error = None
        session.add(run)
        for email_id in email_ids:
            session.add(ProcessedEmail(email_id=email_id, run_id=run_id))


async def mark_run_hold(*, session: AsyncSession, run_id: int, error: str) -> None:
    async with session.begin():
        run = await session.get(Run, run_id)
        if run is None:
            raise ValueError(f"Run {run_id} not found")
        run.status = "hold"
        run.error = error
        session.add(run)
