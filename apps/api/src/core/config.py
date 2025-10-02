"""Application configuration."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields from .env
    )

    # Database configuration (from Story 1.2)
    DATABASE_URL: str

    # GitHub API configuration (Story 1.3)
    GITHUB_TOKEN: Optional[str] = None

    # LLM Provider Configuration (Story 1.7)
    LLM_PROVIDER: str = "ollama"  # 'ollama' or 'openai'

    # OLLAMA Configuration (Local)
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_EXTRACTION_MODEL: str = "qwen2.5:3b"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    OLLAMA_EMBEDDING_DIMENSION: int = 768
    OLLAMA_TIMEOUT: int = 30

    # LiteLLM Proxy Configuration (Remote)
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EXTRACTION_MODEL: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: Optional[str] = None
    OPENAI_EMBEDDING_DIMENSION: int = 1536
    OPENAI_TIMEOUT: int = 30

    @property
    def embedding_dimension(self) -> int:
        """Get embedding dimension based on selected provider."""
        if self.LLM_PROVIDER == "ollama":
            return self.OLLAMA_EMBEDDING_DIMENSION
        elif self.LLM_PROVIDER == "openai":
            return self.OPENAI_EMBEDDING_DIMENSION
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {self.LLM_PROVIDER}")

    @property
    def extraction_model(self) -> str:
        """Get extraction model based on selected provider."""
        if self.LLM_PROVIDER == "ollama":
            return self.OLLAMA_EXTRACTION_MODEL
        elif self.LLM_PROVIDER == "openai":
            if not self.OPENAI_EXTRACTION_MODEL:
                raise ValueError("OPENAI_EXTRACTION_MODEL not configured")
            return self.OPENAI_EXTRACTION_MODEL
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {self.LLM_PROVIDER}")

    @property
    def embedding_model(self) -> str:
        """Get embedding model based on selected provider."""
        if self.LLM_PROVIDER == "ollama":
            return self.OLLAMA_EMBEDDING_MODEL
        elif self.LLM_PROVIDER == "openai":
            if not self.OPENAI_EMBEDDING_MODEL:
                raise ValueError("OPENAI_EMBEDDING_MODEL not configured")
            return self.OPENAI_EMBEDDING_MODEL
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {self.LLM_PROVIDER}")


# Global settings instance
settings = Settings()
