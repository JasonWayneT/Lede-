"""Shared test fixtures — Story 12.1."""

from __future__ import annotations

import pytest

from app.core.config import AppConfig
from app.pipeline.handoff import HandoffPacket


# ---------------------------------------------------------------------------
# Autouse: prevent real OS keychain writes in any test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_keyring(monkeypatch):
    monkeypatch.setattr("keyring.get_password", lambda *a: None)
    monkeypatch.setattr("keyring.set_password", lambda *a: None)
    monkeypatch.setattr("keyring.delete_password", lambda *a: None)


# ---------------------------------------------------------------------------
# Shared config fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def config(tmp_path):
    return AppConfig.model_validate({
        "llm_provider": "ollama",
        "BRIEFING_DATA_DIR": str(tmp_path),
    })


# ---------------------------------------------------------------------------
# Shared HandoffPacket fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_packet():
    packet = HandoffPacket(run_id=1)
    packet.emails = [
        {"email_id": "msg-1", "text": "AI is transforming work.", "title": "AI Weekly",
         "sender_name": "Axios", "date": "2026-01-01"},
    ]
    packet.extracted_texts = [
        {"email_id": "msg-1", "text": "AI is transforming work.", "title": "AI Weekly",
         "sender_name": "Axios", "date": "2026-01-01"},
    ]
    packet.embeddings = [[0.1, 0.2, 0.3]]
    packet.clusters = [packet.extracted_texts]
    packet.selected_clusters = [{"section": "AI", "cluster": packet.extracted_texts}]
    packet.framed_stories = [{
        "section_name": "AI", "depth_tier": "standard", "cluster": packet.extracted_texts,
        "lead_angle": "How AI is changing work.", "local_stakes": "Productivity.",
        "guardrails": [], "source_names": ["Axios"],
    }]
    packet.drafted_stories = [{
        "section_name": "AI", "depth_tier": "standard",
        "prose": "AI is transforming how we work, say researchers.",
        "sources": ["Axios"], "source_count": 1,
    }]
    packet.assembled_markdown = "# Briefing\n\nAI is transforming work."
    packet.tts_script = " ".join(["word"] * 300)
    packet.pronunciation_guide = {}
    packet.markdown_path = "/tmp/briefing.md"
    packet.qa_passed = True
    return packet
