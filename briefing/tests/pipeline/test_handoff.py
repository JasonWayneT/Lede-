"""Tests for HandoffPacket schema and disk I/O — Story 4.1."""

from __future__ import annotations

import pytest

from app.pipeline.handoff import HandoffPacket, read_packet, write_packet


def test_round_trip(tmp_path):
    packet = HandoffPacket(run_id=1, assembled_markdown="hello", qa_passed=True)
    path = write_packet(packet, tmp_path, stage_num=3, stage_name="embed")
    assert path.name == "stage_03_embed.json"
    loaded = read_packet(path)
    assert loaded.run_id == 1
    assert loaded.assembled_markdown == "hello"
    assert loaded.qa_passed is True


def test_directory_created(tmp_path):
    packet = HandoffPacket(run_id=42)
    nested = tmp_path / "artifacts"
    write_packet(packet, nested, stage_num=1, stage_name="ingest")
    assert (nested / "42" / "stage_01_ingest.json").exists()


def test_file_path_pattern(tmp_path):
    packet = HandoffPacket(run_id=7)
    path = write_packet(packet, tmp_path, stage_num=9, stage_name="assemble")
    assert path.name == "stage_09_assemble.json"


def test_defaults():
    p = HandoffPacket(run_id=1)
    assert p.emails == []
    assert p.early_halt is False
    assert p.qa_passed is False


def test_numpy_embeddings_serialized(tmp_path):
    import numpy as np
    packet = HandoffPacket(run_id=1)
    packet.embeddings = [np.array([0.1, 0.2, 0.3], dtype=np.float32)]
    path = write_packet(packet, tmp_path, stage_num=3, stage_name="embed")
    loaded = read_packet(path)
    assert isinstance(loaded.embeddings[0], list)
    assert abs(loaded.embeddings[0][0] - 0.1) < 1e-5
