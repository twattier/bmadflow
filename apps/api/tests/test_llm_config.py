"""Integration tests for LLM provider configuration (Story 1.7)."""

import pytest
import os
from src.core.config import Settings


def test_ollama_provider_config():
    """Test OLLAMA provider configuration loads from environment."""
    # Load from actual environment (uses .env defaults)
    settings = Settings()

    # Should default to OLLAMA
    assert settings.LLM_PROVIDER in ["ollama", "openai"]

    if settings.LLM_PROVIDER == "ollama":
        # Verify OLLAMA configuration from environment
        assert settings.OLLAMA_BASE_URL is not None
        assert settings.OLLAMA_EXTRACTION_MODEL is not None
        assert settings.OLLAMA_EMBEDDING_MODEL is not None
        assert settings.OLLAMA_EMBEDDING_DIMENSION > 0

        # Verify property methods work
        assert settings.embedding_dimension == settings.OLLAMA_EMBEDDING_DIMENSION
        assert settings.extraction_model == settings.OLLAMA_EXTRACTION_MODEL
        assert settings.embedding_model == settings.OLLAMA_EMBEDDING_MODEL


def test_openai_provider_config():
    """Test OpenAI/LiteLLM provider can be configured."""
    # Override environment to test OpenAI provider
    settings = Settings(
        LLM_PROVIDER="openai",
        OPENAI_BASE_URL=os.getenv("OPENAI_BASE_URL", "https://example.com"),
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", "test-key"),
        OPENAI_EXTRACTION_MODEL=os.getenv("OPENAI_EXTRACTION_MODEL", "gpt-4"),
        OPENAI_EMBEDDING_MODEL=os.getenv("OPENAI_EMBEDDING_MODEL", "ada-002"),
    )

    # Verify provider selection
    assert settings.LLM_PROVIDER == "openai"

    # Verify OpenAI configuration
    assert settings.OPENAI_BASE_URL is not None
    assert settings.OPENAI_API_KEY is not None
    assert settings.OPENAI_EXTRACTION_MODEL is not None
    assert settings.OPENAI_EMBEDDING_MODEL is not None

    # Verify property methods work
    assert settings.embedding_dimension == settings.OPENAI_EMBEDDING_DIMENSION
    assert settings.extraction_model == settings.OPENAI_EXTRACTION_MODEL
    assert settings.embedding_model == settings.OPENAI_EMBEDDING_MODEL


def test_embedding_dimension_auto_derives():
    """Test embedding dimension auto-derives from provider selection."""
    # Load actual settings
    settings = Settings()

    # Verify auto-derivation works based on actual LLM_PROVIDER
    if settings.LLM_PROVIDER == "ollama":
        assert settings.embedding_dimension == settings.OLLAMA_EMBEDDING_DIMENSION
    elif settings.LLM_PROVIDER == "openai":
        assert settings.embedding_dimension == settings.OPENAI_EMBEDDING_DIMENSION


def test_invalid_provider_raises_error():
    """Test invalid provider raises ValueError."""
    settings = Settings(LLM_PROVIDER="invalid_provider")

    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        _ = settings.embedding_dimension


def test_default_values():
    """Test default configuration values are sensible."""
    settings = Settings()

    # Should have a valid provider
    assert settings.LLM_PROVIDER in ["ollama", "openai"]

    # Should have valid timeout values
    assert settings.OLLAMA_TIMEOUT > 0
    assert settings.OPENAI_TIMEOUT > 0

    # Should have valid embedding dimensions
    assert settings.OLLAMA_EMBEDDING_DIMENSION > 0
    assert settings.OPENAI_EMBEDDING_DIMENSION > 0
