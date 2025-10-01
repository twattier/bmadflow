"""Application configuration."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env
    )

    # Database configuration (from Story 1.2)
    DATABASE_URL: str

    # GitHub API configuration (Story 1.3)
    GITHUB_TOKEN: Optional[str] = None


# Global settings instance
settings = Settings()
