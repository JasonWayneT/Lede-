from pathlib import Path

import pytest
from pydantic import ValidationError


def test_app_config_defaults():
    from app.core.config import AppConfig

    config = AppConfig()

    assert config.data_dir == Path("./data")
    assert config.log_level == "INFO"
    assert config.llm_provider == "ollama"
    assert config.briefing_depth == "standard"
    assert config.ollama_model_name == "llama3.2"
    assert config.ollama_base_url == "http://localhost:11434"
    assert config.similarity_threshold == 0.75
    assert config.gmail_label == "Newsletters"
    assert config.sections == ["AI", "Technology", "Finance", "Politics", "Other"]


@pytest.mark.parametrize(
    "provider",
    ["ollama", "openai", "anthropic", "gemini", "mcp_sampling"],
)
def test_llm_provider_accepts_valid_values(monkeypatch: pytest.MonkeyPatch, provider: str):
    from app.core.config import AppConfig

    monkeypatch.setenv("LLM_PROVIDER", provider)
    assert AppConfig().llm_provider == provider


def test_llm_provider_rejects_invalid_value(monkeypatch: pytest.MonkeyPatch):
    from app.core.config import AppConfig

    monkeypatch.setenv("LLM_PROVIDER", "not_a_provider")
    with pytest.raises(ValidationError) as excinfo:
        AppConfig()

    msg = str(excinfo.value)
    assert "not_a_provider" in msg
    assert "ollama" in msg
    assert "mcp_sampling" in msg


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR"])
def test_log_level_accepts_valid_values(monkeypatch: pytest.MonkeyPatch, level: str):
    from app.core.config import AppConfig

    monkeypatch.setenv("LOG_LEVEL", level)
    assert AppConfig().log_level == level


def test_log_level_rejects_invalid_value(monkeypatch: pytest.MonkeyPatch):
    from app.core.config import AppConfig

    monkeypatch.setenv("LOG_LEVEL", "LOUD")
    with pytest.raises(ValidationError) as excinfo:
        AppConfig()

    msg = str(excinfo.value)
    assert "LOUD" in msg
    assert "DEBUG" in msg
    assert "ERROR" in msg


@pytest.mark.parametrize("depth", ["brief", "standard", "deep"])
def test_briefing_depth_accepts_valid_values(monkeypatch: pytest.MonkeyPatch, depth: str):
    from app.core.config import AppConfig

    monkeypatch.setenv("BRIEFING_DEPTH", depth)
    assert AppConfig().briefing_depth == depth


def test_briefing_depth_rejects_invalid_value(monkeypatch: pytest.MonkeyPatch):
    from app.core.config import AppConfig

    monkeypatch.setenv("BRIEFING_DEPTH", "mega")
    with pytest.raises(ValidationError) as excinfo:
        AppConfig()

    msg = str(excinfo.value)
    assert "mega" in msg
    assert "brief" in msg
    assert "deep" in msg


def test_data_dir_reads_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from app.core.config import AppConfig

    monkeypatch.setenv("BRIEFING_DATA_DIR", str(tmp_path))
    assert AppConfig().data_dir == tmp_path


def test_sections_parses_comma_separated_and_appends_other(monkeypatch: pytest.MonkeyPatch):
    from app.core.config import AppConfig

    monkeypatch.setenv("BRIEFING_SECTIONS", "AI, Technology ,Finance")
    assert AppConfig().sections == ["AI", "Technology", "Finance", "Other"]

