"""Integration tests for LLM provider configuration (Story 1.7)."""

import pytest
from src.core.config import Settings


def test_ollama_provider_config():
    """Test OLLAMA provider configuration loads correctly."""
    # Create settings with OLLAMA provider
    settings = Settings(
        DATABASE_URL="postgresql://test",
        LLM_PROVIDER="ollama",
        OLLAMA_BASE_URL="http://ollama:11434",
        OLLAMA_EXTRACTION_MODEL="qwen2.5:3b",
        OLLAMA_EMBEDDING_MODEL="nomic-embed-text",
        OLLAMA_EMBEDDING_DIMENSION=768
    )

    # Verify provider selection
    assert settings.LLM_PROVIDER == "ollama"

    # Verify OLLAMA configuration
    assert settings.OLLAMA_BASE_URL == "http://ollama:11434"
    assert settings.OLLAMA_EXTRACTION_MODEL == "qwen2.5:3b"
    assert settings.OLLAMA_EMBEDDING_MODEL == "nomic-embed-text"
    assert settings.OLLAMA_EMBEDDING_DIMENSION == 768

    # Verify property methods
    assert settings.embedding_dimension == 768
    assert settings.extraction_model == "qwen2.5:3b"
    assert settings.embedding_model == "nomic-embed-text"


def test_openai_provider_config():
    """Test OpenAI/LiteLLM provider configuration loads correctly."""
    # Create settings with OpenAI provider
    settings = Settings(
        DATABASE_URL="postgresql://test",
        LLM_PROVIDER="openai",
        OPENAI_BASE_URL="https://llmproxy.ai.orange",
        OPENAI_API_KEY="sk-test-key",
        OPENAI_EXTRACTION_MODEL="openai/gpt-4.1",
        OPENAI_EMBEDDING_MODEL="openai/text-embedding-ada-002",
        OPENAI_EMBEDDING_DIMENSION=1536
    )

    # Verify provider selection
    assert settings.LLM_PROVIDER == "openai"

    # Verify OpenAI configuration
    assert settings.OPENAI_BASE_URL == "https://llmproxy.ai.orange"
    assert settings.OPENAI_API_KEY == "sk-test-key"
    assert settings.OPENAI_EXTRACTION_MODEL == "openai/gpt-4.1"
    assert settings.OPENAI_EMBEDDING_MODEL == "openai/text-embedding-ada-002"
    assert settings.OPENAI_EMBEDDING_DIMENSION == 1536

    # Verify property methods
    assert settings.embedding_dimension == 1536
    assert settings.extraction_model == "openai/gpt-4.1"
    assert settings.embedding_model == "openai/text-embedding-ada-002"


def test_embedding_dimension_auto_derives():
    """Test embedding dimension auto-derives from provider selection."""
    # OLLAMA should give 768
    ollama_settings = Settings(
        DATABASE_URL="postgresql://test",
        LLM_PROVIDER="ollama",
        OLLAMA_EMBEDDING_DIMENSION=768,
        OPENAI_EMBEDDING_DIMENSION=1536
    )
    assert ollama_settings.embedding_dimension == 768

    # OpenAI should give 1536
    openai_settings = Settings(
        DATABASE_URL="postgresql://test",
        LLM_PROVIDER="openai",
        OPENAI_EXTRACTION_MODEL="gpt-4",
        OPENAI_EMBEDDING_MODEL="ada-002",
        OLLAMA_EMBEDDING_DIMENSION=768,
        OPENAI_EMBEDDING_DIMENSION=1536
    )
    assert openai_settings.embedding_dimension == 1536


def test_invalid_provider_raises_error():
    """Test invalid provider raises ValueError."""
    settings = Settings(
        DATABASE_URL="postgresql://test",
        LLM_PROVIDER="invalid_provider"
    )

    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        _ = settings.embedding_dimension


def test_openai_properties_require_config():
    """Test OpenAI provider properties require configuration."""
    settings = Settings(
        DATABASE_URL="postgresql://test",
        LLM_PROVIDER="openai",
        OPENAI_EXTRACTION_MODEL="gpt-4",
        OPENAI_EMBEDDING_MODEL="ada-002"
    )

    # Should work when configured
    assert settings.extraction_model == "gpt-4"
    assert settings.embedding_model == "ada-002"


def test_default_values():
    """Test default configuration values."""
    settings = Settings(
        DATABASE_URL="postgresql://test"
    )

    # Default provider should be ollama
    assert settings.LLM_PROVIDER == "ollama"

    # Default OLLAMA values
    assert settings.OLLAMA_BASE_URL == "http://ollama:11434"
    assert settings.OLLAMA_EXTRACTION_MODEL == "qwen2.5:3b"
    assert settings.OLLAMA_EMBEDDING_MODEL == "nomic-embed-text"
    assert settings.OLLAMA_EMBEDDING_DIMENSION == 768
    assert settings.OLLAMA_TIMEOUT == 30

    # Default OpenAI values
    assert settings.OPENAI_EMBEDDING_DIMENSION == 1536
    assert settings.OPENAI_TIMEOUT == 30
