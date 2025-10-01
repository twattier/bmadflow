"""Application configuration."""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database configuration (from Story 1.2)
    DATABASE_URL: str

    # GitHub API configuration (Story 1.3)
    GITHUB_TOKEN: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
