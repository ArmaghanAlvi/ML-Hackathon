"""config.py

Owner: Stream C · Roadmap: Stage 4a
Purpose: settings loaded from environment / .env (keys mirror .env.example).
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SERPAPI_KEY: str = ""
    USE_MOCK_RESPONSE: bool = True
    DEMO_CACHED: bool = False
    CACHE_DIR: str = "backend/app/cache"
    THRESHOLDS_PATH: str = "ml/artifacts/thresholds.json"
    CORS_ORIGINS: str = "http://localhost:5173"  # comma-separated
    HF_MATCHER_REPO: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
