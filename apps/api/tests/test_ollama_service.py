"""Unit tests for OLLAMA service integration (Story 2.1)."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from src.services.ollama_service import OllamaService, OllamaConfig


@pytest.fixture
def ollama_config():
    """Fixture for OLLAMA service configuration."""
    return OllamaConfig(
        host="http://localhost:11434",
        model="qwen2.5:7b-instruct-q4_K_M",
        timeout=30.0,
        max_retries=3,
        retry_delay=1.0,
    )


@pytest.fixture
def ollama_service(ollama_config):
    """Fixture for OLLAMA service instance."""
    return OllamaService(config=ollama_config)


@pytest.mark.asyncio
async def test_ollama_service_initialization(ollama_config):
    """Test OLLAMA service initializes with correct configuration."""
    service = OllamaService(config=ollama_config)

    assert service.config.host == "http://localhost:11434"
    assert service.config.model == "qwen2.5:7b-instruct-q4_K_M"
    assert service.config.timeout == 30.0
    assert service.config.max_retries == 3
    assert service.client is not None


@pytest.mark.asyncio
async def test_ollama_service_default_config():
    """Test OLLAMA service uses default configuration when none provided."""
    service = OllamaService()

    assert service.config.host == "http://localhost:11434"
    assert service.config.model == "qwen2.5:7b-instruct-q4_K_M"
    assert service.config.timeout == 30.0


@pytest.mark.asyncio
async def test_generate_success(ollama_service):
    """Test successful LLM generation returns expected response."""
    mock_response = {
        "message": {"content": "Test response content"},
        "model": "qwen2.5:7b-instruct-q4_K_M",
        "created_at": "2025-10-03T00:00:00Z",
        "done": True,
        "total_duration": 1000000,
        "prompt_eval_count": 10,
        "eval_count": 20,
    }

    with patch.object(
        ollama_service, "_generate_sync", return_value=mock_response
    ) as mock_generate:
        response = await ollama_service.generate(
            prompt="Test prompt", system_prompt="Test system"
        )

        assert response["content"] == "Test response content"
        assert response["model"] == "qwen2.5:7b-instruct-q4_K_M"
        assert response["done"] is True
        assert "total_duration" in response
        mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_generate_with_json_format(ollama_service):
    """Test LLM generation with JSON format request."""
    mock_response = {
        "message": {"content": '{"key": "value"}'},
        "model": "qwen2.5:7b-instruct-q4_K_M",
        "created_at": "2025-10-03T00:00:00Z",
        "done": True,
    }

    with patch.object(
        ollama_service, "_generate_sync", return_value=mock_response
    ) as mock_generate:
        response = await ollama_service.generate(
            prompt="Extract JSON", format_json=True
        )

        assert response["content"] == '{"key": "value"}'
        mock_generate.assert_called_once()
        # Verify format_json parameter was passed
        call_args = mock_generate.call_args
        assert call_args[1]["format_json"] is True


@pytest.mark.asyncio
async def test_generate_timeout_retry(ollama_service):
    """Test LLM generation retries on timeout."""
    ollama_service.config.max_retries = 2
    ollama_service.config.retry_delay = 0.1  # Fast retry for testing

    with patch.object(
        ollama_service, "_generate_sync", side_effect=asyncio.TimeoutError()
    ):
        with pytest.raises(Exception) as exc_info:
            await ollama_service.generate(prompt="Test prompt")

        assert "failed after 2 attempts" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_retry_with_eventual_success(ollama_service):
    """Test LLM generation succeeds after initial failures."""
    ollama_service.config.max_retries = 3
    ollama_service.config.retry_delay = 0.1

    mock_response = {
        "message": {"content": "Success after retry"},
        "model": "qwen2.5:7b-instruct-q4_K_M",
        "done": True,
    }

    # Fail twice, then succeed
    side_effects = [
        Exception("Network error"),
        Exception("Temporary failure"),
        mock_response,
    ]

    with patch.object(
        ollama_service, "_generate_sync", side_effect=side_effects
    ) as mock_generate:
        response = await ollama_service.generate(prompt="Test prompt")

        assert response["content"] == "Success after retry"
        assert mock_generate.call_count == 3


@pytest.mark.asyncio
async def test_health_check_success(ollama_service):
    """Test health check succeeds when service and model are available."""
    mock_list_response = {
        "models": [
            {"name": "qwen2.5:7b-instruct-q4_K_M", "size": 4683087332},
            {"name": "nomic-embed-text:latest", "size": 274302450},
        ]
    }

    mock_generate_response = {
        "content": "OK",
        "model": "qwen2.5:7b-instruct-q4_K_M",
        "done": True,
    }

    with patch.object(
        ollama_service.client, "list", return_value=mock_list_response
    ), patch.object(
        ollama_service, "generate", return_value=mock_generate_response
    ) as mock_generate:
        health = await ollama_service.health_check()

        assert health["status"] == "healthy"
        assert health["model"] == "qwen2.5:7b-instruct-q4_K_M"
        assert health["model_loaded"] is True
        assert "qwen2.5:7b-instruct-q4_K_M" in health["available_models"]
        assert "timestamp" in health
        mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_health_check_model_not_loaded(ollama_service):
    """Test health check fails when configured model is not available."""
    mock_list_response = {
        "models": [
            {"name": "other-model:latest", "size": 1000000},
        ]
    }

    with patch.object(ollama_service.client, "list", return_value=mock_list_response):
        with pytest.raises(Exception) as exc_info:
            await ollama_service.health_check()

        assert "not found" in str(exc_info.value)
        assert "qwen2.5:7b-instruct-q4_K_M" in str(exc_info.value)


@pytest.mark.asyncio
async def test_health_check_service_timeout(ollama_service):
    """Test health check fails on service timeout."""

    async def timeout_mock():
        await asyncio.sleep(10)  # Simulate long delay

    with patch.object(ollama_service.client, "list", side_effect=timeout_mock):
        with pytest.raises(Exception) as exc_info:
            await ollama_service.health_check()

        assert "timed out" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_health_check_service_error(ollama_service):
    """Test health check fails when service is unreachable."""
    with patch.object(
        ollama_service.client,
        "list",
        side_effect=Exception("Connection refused"),
    ):
        with pytest.raises(Exception) as exc_info:
            await ollama_service.health_check()

        assert "unhealthy" in str(exc_info.value)
        assert "Connection refused" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_ollama_real_connection():
    """
    Integration test: Verify real OLLAMA connection works.

    This test requires OLLAMA running on localhost:11434 with qwen2.5 model.
    Skipped in CI (use --run-integration flag to enable).
    """
    pytest.skip("Integration test - run manually with --run-integration")

    service = OllamaService()

    # Test health check
    health = await service.health_check()
    assert health["status"] == "healthy"
    assert health["model_loaded"] is True

    # Test actual generation
    response = await service.generate(
        prompt="What is 2+2? Answer with just the number.",
        system_prompt="You are a math assistant. Be concise.",
    )

    assert response["content"] is not None
    assert len(response["content"]) > 0
    assert response["done"] is True
