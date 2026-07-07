"""Tests for app/pipeline/ordering.py — CR-005, FR-030."""

from __future__ import annotations

from app.core.config import AppConfig
from app.pipeline.ordering import order_stories_by_section


def _cfg():
    return AppConfig(llm_provider="ollama")  # default sections: AI, Technology, Finance, Politics, Other


def test_sections_follow_config_order_other_last():
    stories = [
        {"section_name": "Other", "source_count": 1},
        {"section_name": "Finance", "source_count": 1},
        {"section_name": "AI", "source_count": 1},
    ]
    names = [sec for sec, _ in order_stories_by_section(stories, _cfg())]
    assert names.index("AI") < names.index("Finance") < names.index("Other")


def test_stories_sorted_by_source_count_desc():
    stories = [
        {"section_name": "AI", "source_count": 1, "prose": "low"},
        {"section_name": "AI", "source_count": 5, "prose": "high"},
    ]
    ordered = order_stories_by_section(stories, _cfg())
    ai_stories = next(st for sec, st in ordered if sec == "AI")
    assert ai_stories[0]["source_count"] == 5
    assert ai_stories[1]["source_count"] == 1


def test_unknown_section_appended_last():
    stories = [
        {"section_name": "AI", "source_count": 1},
        {"section_name": "Sports", "source_count": 1},
    ]
    names = [sec for sec, _ in order_stories_by_section(stories, _cfg())]
    assert names == ["AI", "Sports"]  # Sports (unmapped) appended after config sections
