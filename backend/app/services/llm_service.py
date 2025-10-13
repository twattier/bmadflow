"""LLM service for multi-provider abstraction."""

import logging
import os
from typing import Dict, List
from uuid import UUID

import httpx
import ollama
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings
from app.models.llm_provider import LLMProvider, LLMProviderName
from app.repositories.llm_provider_repository import LLMProviderRepository

logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Custom exception for LLM provider errors."""

    pass


class LLMService:
    """Abstraction over multiple LLM providers."""

    def __init__(self):
        """Initialize LLM service."""
        self.timeout = 60.0  # 60s timeout for LLM calls

    async def generate_completion(
        self, llm_provider_id: UUID, messages: List[Dict[str, str]], db: AsyncSession
    ) -> str:
        """Generate LLM completion using specified provider.

        Args:
            llm_provider_id: UUID of LLM provider from llm_providers table
            messages: List of message dicts [{"role": "system/user/assistant", "content": "..."}]
            db: Database session

        Returns:
            Generated text response

        Raises:
            ValueError: If provider not found or unsupported
            LLMProviderError: If LLM API call fails
        """
        # Fetch provider config from database
        provider_repo = LLMProviderRepository(db)
        provider = await provider_repo.get_by_id(llm_provider_id)

        if not provider:
            raise ValueError(f"LLM provider not found: {llm_provider_id}")

        logger.info(
            f"Generating completion using provider: {provider.provider_name} "
            f"(model: {provider.model_name})"
        )

        # Route to appropriate provider client
        try:
            if provider.provider_name == LLMProviderName.OPENAI:
                response = await self._call_openai(provider, messages)
            elif provider.provider_name == LLMProviderName.GOOGLE:
                response = await self._call_google(provider, messages)
            elif provider.provider_name == LLMProviderName.LITELLM:
                response = await self._call_litellm(provider, messages)
            elif provider.provider_name == LLMProviderName.OLLAMA:
                response = await self._call_ollama(provider, messages)
            else:
                raise ValueError(f"Unsupported provider: {provider.provider_name}")

            logger.info(f"Completion generated successfully ({len(response)} chars)")
            return response

        except (RetryError, LLMProviderError) as e:
            logger.error(f"LLM completion failed after retries: {e}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error in LLM completion: {e}"
            logger.error(error_msg, exc_info=True)
            raise LLMProviderError(error_msg) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True,
    )
    async def _call_openai(self, provider: LLMProvider, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API with retry logic.

        Args:
            provider: LLM provider config
            messages: Message list

        Returns:
            Generated text response

        Raises:
            LLMProviderError: If API call fails
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMProviderError("OPENAI_API_KEY not found in environment")

        try:
            # Import openai library
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise LLMProviderError("openai library not installed. Run: pip install openai")

            client = AsyncOpenAI(api_key=api_key, timeout=self.timeout)

            # Call OpenAI Chat API
            response = await client.chat.completions.create(
                model=provider.model_name,
                messages=messages,
                temperature=(
                    provider.api_config.get("temperature", 0.7) if provider.api_config else 0.7
                ),
                max_tokens=(
                    provider.api_config.get("max_tokens", 2000) if provider.api_config else 2000
                ),
            )

            return response.choices[0].message.content

        except Exception as e:
            raise LLMProviderError(f"OpenAI API error: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True,
    )
    async def _call_google(self, provider: LLMProvider, messages: List[Dict[str, str]]) -> str:
        """Call Google Gemini API with retry logic.

        Args:
            provider: LLM provider config
            messages: Message list

        Returns:
            Generated text response

        Raises:
            LLMProviderError: If API call fails
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise LLMProviderError("GOOGLE_API_KEY not found in environment")

        try:
            # Import google-generativeai library
            try:
                import google.generativeai as genai
            except ImportError:
                raise LLMProviderError(
                    "google-generativeai library not installed. "
                    "Run: pip install google-generativeai"
                )

            genai.configure(api_key=api_key)

            # Convert messages to Gemini format (system + user messages)
            system_parts = [msg["content"] for msg in messages if msg["role"] == "system"]
            user_parts = [msg["content"] for msg in messages if msg["role"] == "user"]
            context = "\n\n".join(system_parts + user_parts)

            # Call Gemini API
            model = genai.GenerativeModel(provider.model_name)
            response = model.generate_content(
                context,
                generation_config={
                    "temperature": (
                        provider.api_config.get("temperature", 0.7) if provider.api_config else 0.7
                    ),
                    "max_output_tokens": (
                        provider.api_config.get("max_tokens", 2000) if provider.api_config else 2000
                    ),
                },
            )

            return response.text

        except Exception as e:
            raise LLMProviderError(f"Google Gemini API error: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True,
    )
    async def _call_litellm(self, provider: LLMProvider, messages: List[Dict[str, str]]) -> str:
        """Call LiteLLM API with retry logic.

        Args:
            provider: LLM provider config
            messages: Message list

        Returns:
            Generated text response

        Raises:
            LLMProviderError: If API call fails
        """
        try:
            # Import litellm library
            try:
                from litellm import acompletion
            except ImportError:
                raise LLMProviderError("litellm library not installed. Run: pip install litellm")

            # Call LiteLLM (supports multiple providers via unified interface)
            response = await acompletion(
                model=provider.model_name,
                messages=messages,
                temperature=(
                    provider.api_config.get("temperature", 0.7) if provider.api_config else 0.7
                ),
                max_tokens=(
                    provider.api_config.get("max_tokens", 2000) if provider.api_config else 2000
                ),
                timeout=self.timeout,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise LLMProviderError(f"LiteLLM API error: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    async def _call_ollama(self, provider: LLMProvider, messages: List[Dict[str, str]]) -> str:
        """Call Ollama API with retry logic.

        Args:
            provider: LLM provider config
            messages: Message list

        Returns:
            Generated text response

        Raises:
            LLMProviderError: If API call fails
        """
        try:
            # Configure Ollama client
            ollama_endpoint = settings.ollama_endpoint_url
            if ollama_endpoint != "http://localhost:11434":
                client = ollama.Client(host=ollama_endpoint)
            else:
                client = ollama

            # Call Ollama Chat API
            response = client.chat(
                model=provider.model_name,
                messages=messages,
                options={
                    "temperature": (
                        provider.api_config.get("temperature", 0.7) if provider.api_config else 0.7
                    ),
                    "num_predict": (
                        provider.api_config.get("max_tokens", 2000) if provider.api_config else 2000
                    ),
                },
            )

            return response["message"]["content"]

        except Exception as e:
            raise LLMProviderError(f"Ollama API error: {e}") from e
