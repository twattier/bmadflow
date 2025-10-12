"""Application configuration using Pydantic Settings."""

from pathlib import Path

from pydantic_settings import BaseSettings

# Get project root directory (parent of backend/)
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str
    backend_port: int = 8000
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    ollama_endpoint_url: str = "http://localhost:11434"
    embedding_model_name: str = "nomic-embed-text"
    embedding_batch_size: int = 10

    model_config = {
        "env_file": str(PROJECT_ROOT / ".env"),
        "extra": "ignore",  # Ignore extra fields in .env
    }


settings = Settings()
