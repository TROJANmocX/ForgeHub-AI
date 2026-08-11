"""
ForgeHub AI — Application Configuration
Reads settings from environment / .env file.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Demo / runtime mode
    demo_mode: bool = True

    # DataHub
    datahub_url: str = "http://localhost:8080"
    datahub_token: str = ""

    # LLM
    llm_provider: Literal["mock", "anthropic", "openai", "gemini"] = "mock"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""

    # Generation
    max_repair_attempts: int = 3

    # CORS
    frontend_origin: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
