"""HandoffPacket dataclass and disk I/O helpers."""

# Implements ARCH-003, DATA-001

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class HandoffPacket:
    run_id: int
    emails: list = field(default_factory=list)
    extracted_texts: list = field(default_factory=list)
    embeddings: list = field(default_factory=list)
    clusters: list = field(default_factory=list)
    selected_clusters: list = field(default_factory=list)
    framed_stories: list = field(default_factory=list)
    drafted_stories: list = field(default_factory=list)
    assembled_markdown: str = ""
    tts_script: str = ""
    pronunciation_guide: dict = field(default_factory=dict)
    qa_passed: bool = False
    errors: list = field(default_factory=list)
    early_halt: bool = False
    halt_reason: str = ""
    markdown_path: str = ""


def _serialize(obj: object) -> object:
    import datetime
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Not serializable: {type(obj)}")


def write_packet(
    packet: HandoffPacket,
    artifacts_dir: Path,
    stage_num: int,
    stage_name: str,
) -> Path:
    run_dir = artifacts_dir / str(packet.run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / f"stage_{stage_num:02d}_{stage_name}.json"
    path.write_text(json.dumps(dataclasses.asdict(packet), default=_serialize), encoding="utf-8")
    return path


def read_packet(path: Path) -> HandoffPacket:
    data = json.loads(path.read_text(encoding="utf-8"))
    return HandoffPacket(**data)
