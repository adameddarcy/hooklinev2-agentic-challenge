"""Application settings, loaded from the environment (prefix ``HOOKLINE_``)."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the service."""

    model_config = SettingsConfigDict(env_prefix="HOOKLINE_", env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./hookline.db"
    delivery_timeout_seconds: float = Field(default=5.0, gt=0, le=30)
    user_agent: str = "Hookline/0.1"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings()
