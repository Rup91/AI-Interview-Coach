"""Application configuration.

Settings are sourced from environment variables (and an optional .env file)
so that no configurable value is hardcoded in source, per CLAUDE.md's
Configuration guideline.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Interview Coach API"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    # Business rule (not client-controlled): every interview asks at least
    # this many questions, and may continue up to this many based on the
    # candidate's performance. See app.business.interview_service.
    min_interview_questions: int = 6
    max_interview_questions: int = 12

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Cached via lru_cache so environment variables are read once per process
    instead of on every request.
    """
    return Settings()
