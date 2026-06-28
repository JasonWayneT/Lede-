"""Core configuration model and environment loading."""

# Implements ARCH-002

from __future__ import annotations

from pathlib import Path

from pydantic import Field, PrivateAttr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration loaded from environment variables and `.env`."""

    # Filesystem / runtime
    data_dir: Path = Field(default=Path("./data"), validation_alias="BRIEFING_DATA_DIR")

    # Logging
    log_level: str = "INFO"

    # LLM provider
    llm_provider: str = "ollama"
    ollama_model_name: str = "llama3.1:8b-instruct-q5_K_M"
    ollama_base_url: str = "http://localhost:11434"
    openai_model_name: str = "gpt-4o-mini"
    anthropic_model_name: str = "claude-haiku-4-5-20251001"
    gemini_model_name: str = "gemini-1.5-flash"

    # TTS engine
    tts_engine: str = "kokoro"

    # Retry context — set by orchestrator during retry tiers; not loaded from env
    _retry_context: dict = PrivateAttr(default_factory=dict)

    # Pipeline settings
    similarity_threshold: float = 0.75
    briefing_depth: str = "standard"

    # Gmail ingest
    gmail_label: str = "Newsletters"

    # Editorial taxonomy
    sections: list[str] = Field(
        default_factory=lambda: ["AI", "Technology", "Finance", "Politics", "Other"],
        validation_alias="BRIEFING_SECTIONS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
        enable_decoding=False,
    )

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if v not in valid:
            raise ValueError(f"Invalid log_level '{v}'. Must be one of: {sorted(valid)}")
        return v

    @field_validator("llm_provider")
    @classmethod
    def _validate_llm_provider(cls, v: str) -> str:
        valid = {"ollama", "openai", "anthropic", "gemini", "mcp_sampling"}
        if v not in valid:
            raise ValueError(f"Invalid llm_provider '{v}'. Must be one of: {sorted(valid)}")
        return v

    @field_validator("briefing_depth")
    @classmethod
    def _validate_briefing_depth(cls, v: str) -> str:
        valid = {"brief", "standard", "deep"}
        if v not in valid:
            raise ValueError(f"Invalid briefing_depth '{v}'. Must be one of: {sorted(valid)}")
        return v

    @field_validator("sections", mode="before")
    @classmethod
    def _parse_sections(cls, v: object) -> list[str]:
        if v is None:
            return ["AI", "Technology", "Finance", "Politics", "Other"]

        if isinstance(v, str):
            parts = [p.strip() for p in v.split(",")]
            sections = [p for p in parts if p]
        elif isinstance(v, list):
            sections = [str(p).strip() for p in v if str(p).strip()]
        else:
            sections = [str(v).strip()] if str(v).strip() else []

        if "Other" not in sections:
            sections.append("Other")

        return sections

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Prefer environment variables over `.env`, so test overrides (monkeypatch) win.
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

