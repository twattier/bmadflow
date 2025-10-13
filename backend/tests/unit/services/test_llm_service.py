"""Unit tests for LLM Service."""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.llm_provider import LLMProvider, LLMProviderName
from app.services.llm_service import LLMProviderError, LLMService


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def openai_provider():
    """Sample OpenAI provider."""
    provider = MagicMock(spec=LLMProvider)
    provider.id = uuid4()
    provider.provider_name = LLMProviderName.OPENAI
    provider.model_name = "gpt-4"
    provider.api_config = {"temperature": 0.7, "max_tokens": 2000}
    return provider


@pytest.fixture
def google_provider():
    """Sample Google provider."""
    provider = MagicMock(spec=LLMProvider)
    provider.id = uuid4()
    provider.provider_name = LLMProviderName.GOOGLE
    provider.model_name = "gemini-pro"
    provider.api_config = {"temperature": 0.7, "max_tokens": 2000}
    return provider


@pytest.fixture
def ollama_provider():
    """Sample Ollama provider."""
    provider = MagicMock(spec=LLMProvider)
    provider.id = uuid4()
    provider.provider_name = LLMProviderName.OLLAMA
    provider.model_name = "llama2"
    provider.api_config = None
    return provider


@pytest.fixture
def litellm_provider():
    """Sample LiteLLM provider."""
    provider = MagicMock(spec=LLMProvider)
    provider.id = uuid4()
    provider.provider_name = LLMProviderName.LITELLM
    provider.model_name = "gpt-3.5-turbo"
    provider.api_config = {"temperature": 0.7}
    return provider


@pytest.fixture
def sample_messages():
    """Sample message list."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are the project goals?"},
    ]


@pytest.mark.asyncio
async def test_llm_service_provider_not_found(mock_db):
    """Test LLMService raises ValueError if provider not found."""
    # Arrange
    service = LLMService()
    provider_id = uuid4()

    with patch("app.services.llm_service.LLMProviderRepository") as mock_repo:
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = None
        mock_repo.return_value = mock_repo_instance

        # Act & Assert
        with pytest.raises(ValueError, match="LLM provider not found"):
            await service.generate_completion(provider_id, [], mock_db)


@pytest.mark.asyncio
async def test_llm_service_call_openai(mock_db, openai_provider, sample_messages):
    """Test LLMService._call_openai() returns completion."""
    # Arrange
    service = LLMService()
    mock_response = "The project goals are..."

    with (
        patch("app.services.llm_service.LLMProviderRepository") as mock_repo,
        patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
    ):

        # Mock repository
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = openai_provider
        mock_repo.return_value = mock_repo_instance

        # Mock OpenAI client (imported inside function)
        with patch("openai.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock(message=MagicMock(content=mock_response))]
            mock_client.chat.completions.create.return_value = mock_completion
            mock_openai.return_value = mock_client

            # Act
            result = await service.generate_completion(openai_provider.id, sample_messages, mock_db)

            # Assert
            assert result == mock_response
            mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_llm_service_call_google(mock_db, google_provider, sample_messages):
    """Test LLMService._call_google() returns completion."""
    # Arrange
    service = LLMService()
    mock_response = "The project goals are..."

    with (
        patch("app.services.llm_service.LLMProviderRepository") as mock_repo,
        patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}),
    ):

        # Mock repository
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = google_provider
        mock_repo.return_value = mock_repo_instance

        # Mock Google Gemini client (imported inside function)
        with patch("google.generativeai.GenerativeModel") as mock_genai_model, \
             patch("google.generativeai.configure"):
            mock_model = MagicMock()
            mock_model.generate_content.return_value = MagicMock(text=mock_response)
            mock_genai_model.return_value = mock_model

            # Act
            result = await service.generate_completion(google_provider.id, sample_messages, mock_db)

            # Assert
            assert result == mock_response
            mock_model.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_llm_service_call_ollama(mock_db, ollama_provider, sample_messages):
    """Test LLMService._call_ollama() returns completion."""
    # Arrange
    service = LLMService()
    mock_response = "The project goals are..."

    with (
        patch("app.services.llm_service.LLMProviderRepository") as mock_repo,
        patch("app.services.llm_service.ollama") as mock_ollama,
    ):

        # Mock repository
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = ollama_provider
        mock_repo.return_value = mock_repo_instance

        # Mock Ollama client
        mock_ollama.chat.return_value = {"message": {"content": mock_response}}

        # Act
        result = await service.generate_completion(ollama_provider.id, sample_messages, mock_db)

        # Assert
        assert result == mock_response
        mock_ollama.chat.assert_called_once()


@pytest.mark.asyncio
async def test_llm_service_call_litellm(mock_db, litellm_provider, sample_messages):
    """Test LLMService._call_litellm() returns completion."""
    # Arrange
    service = LLMService()
    mock_response = "The project goals are..."

    with (
        patch("app.services.llm_service.LLMProviderRepository") as mock_repo,
    ):

        # Mock repository
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = litellm_provider
        mock_repo.return_value = mock_repo_instance

        # Mock LiteLLM module (imported inside function)
        mock_litellm = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=mock_response))]
        mock_acompletion = AsyncMock(return_value=mock_completion)
        mock_litellm.acompletion = mock_acompletion

        with patch.dict("sys.modules", {"litellm": mock_litellm}):
            # Act
            result = await service.generate_completion(litellm_provider.id, sample_messages, mock_db)

            # Assert
            assert result == mock_response
            mock_acompletion.assert_called_once()


@pytest.mark.asyncio
async def test_llm_service_openai_missing_api_key(mock_db, openai_provider, sample_messages):
    """Test LLMService raises error if OPENAI_API_KEY missing."""
    # Arrange
    service = LLMService()

    with (
        patch("app.services.llm_service.LLMProviderRepository") as mock_repo,
        patch.dict(os.environ, {}, clear=True),
    ):

        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = openai_provider
        mock_repo.return_value = mock_repo_instance

        # Act & Assert
        with pytest.raises(LLMProviderError, match="OPENAI_API_KEY not found"):
            await service.generate_completion(openai_provider.id, sample_messages, mock_db)


@pytest.mark.asyncio
async def test_llm_service_unsupported_provider(mock_db, sample_messages):
    """Test LLMService raises error for unsupported provider."""
    # Arrange
    service = LLMService()
    unsupported_provider = MagicMock(spec=LLMProvider)
    unsupported_provider.id = uuid4()
    unsupported_provider.provider_name = "unsupported"
    unsupported_provider.model_name = "test-model"

    with patch("app.services.llm_service.LLMProviderRepository") as mock_repo:
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = unsupported_provider
        mock_repo.return_value = mock_repo_instance

        # Act & Assert
        with pytest.raises(LLMProviderError, match="Unexpected error"):
            await service.generate_completion(unsupported_provider.id, sample_messages, mock_db)
