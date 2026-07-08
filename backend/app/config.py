"""Application configuration."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    bright_data_api_key: str = ""
    database_url: str = "sqlite:///./shoppilot.db"
    backend_cors_origins: str = "http://localhost:3000"

    codex_agents_enabled: bool = False
    codex_mode: str = "subprocess"
    codex_allow_file_patch: bool = False
    codex_require_human_review: bool = True
    codex_timeout_seconds: int = 120

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_bright_data(self) -> bool:
        return bool(self.bright_data_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
