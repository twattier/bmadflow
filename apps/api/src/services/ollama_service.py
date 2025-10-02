"""OLLAMA service for LLM-powered content extraction."""

import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime

import ollama
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class OllamaConfig(BaseModel):
    """Configuration for OLLAMA service."""

    host: str = Field(default="http://localhost:11434", description="OLLAMA API host")
    model: str = Field(
        default="qwen2.5:7b-instruct-q4_K_M", description="LLM model name"
    )
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(
        default=1.0, description="Initial retry delay in seconds (exponential backoff)"
    )


class OllamaService:
    """Service for interacting with OLLAMA LLM for content extraction."""

    def __init__(self, config: Optional[OllamaConfig] = None):
        """Initialize OLLAMA service with configuration."""
        self.config = config or OllamaConfig()
        self.client = ollama.Client(host=self.config.host)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        format_json: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate LLM response with retry logic and timeout handling.

        Args:
            prompt: User prompt for the LLM
            system_prompt: Optional system prompt for context
            format_json: If True, request JSON-formatted response

        Returns:
            Dict containing response and metadata

        Raises:
            Exception: If all retry attempts fail
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                # Use asyncio to run synchronous ollama client with timeout
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._generate_sync,
                        messages=messages,
                        format_json=format_json,
                    ),
                    timeout=self.config.timeout,
                )

                return {
                    "content": response["message"]["content"],
                    "model": response["model"],
                    "created_at": response.get("created_at"),
                    "done": response.get("done", True),
                    "total_duration": response.get("total_duration"),
                    "prompt_eval_count": response.get("prompt_eval_count"),
                    "eval_count": response.get("eval_count"),
                }

            except asyncio.TimeoutError:
                last_error = f"Request timed out after {self.config.timeout}s"
                logger.warning(
                    f"OLLAMA request timeout (attempt {attempt + 1}/{self.config.max_retries})"
                )

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"OLLAMA request failed (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )

            # Exponential backoff before retry
            if attempt < self.config.max_retries - 1:
                delay = self.config.retry_delay * (2**attempt)
                logger.info(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)

        # All retries exhausted
        raise Exception(
            f"OLLAMA request failed after {self.config.max_retries} attempts. Last error: {last_error}"
        )

    def _generate_sync(
        self, messages: list[Dict[str, str]], format_json: bool = False
    ) -> Dict[str, Any]:
        """Synchronous wrapper for ollama.chat call."""
        options = {}
        if format_json:
            options["format"] = "json"

        response = self.client.chat(
            model=self.config.model,
            messages=messages,
            options=options if options else None,
        )

        return response

    async def health_check(self) -> Dict[str, Any]:
        """
        Check OLLAMA service health and model availability.

        Returns:
            Dict with health status, model info, and timestamp

        Raises:
            Exception: If service or model is unavailable
        """
        try:
            # Check if service is responding
            models_response = await asyncio.wait_for(
                asyncio.to_thread(self.client.list), timeout=5.0
            )

            # Check if configured model is available
            available_models = [m["name"] for m in models_response.get("models", [])]
            model_loaded = self.config.model in available_models

            if not model_loaded:
                raise Exception(
                    f"Model '{self.config.model}' not found. Available models: {available_models}"
                )

            # Test inference with simple prompt
            test_response = await self.generate(
                prompt="Respond with 'OK'",
                system_prompt="You are a test assistant. Respond with exactly 'OK'.",
            )

            return {
                "status": "healthy",
                "model": self.config.model,
                "model_loaded": model_loaded,
                "available_models": available_models,
                "test_response": test_response["content"][:50],
                "timestamp": datetime.utcnow().isoformat(),
            }

        except asyncio.TimeoutError:
            raise Exception("OLLAMA service health check timed out")
        except Exception as e:
            raise Exception(f"OLLAMA service unhealthy: {e}")
