"""Embedding service using Ollama for vector generation."""

import logging
from typing import List

import ollama
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Ollama."""

    def __init__(self, ollama_endpoint: str = None, batch_size: int = None):
        """Initialize embedding service.

        Args:
            ollama_endpoint: Ollama API endpoint URL
            batch_size: Number of texts to process per batch
        """
        self.ollama_endpoint = ollama_endpoint or settings.ollama_endpoint_url
        self.batch_size = batch_size or settings.embedding_batch_size
        self.model_name = "nomic-embed-text"
        self.embedding_dim = 768

        # Configure Ollama client
        if self.ollama_endpoint != "http://localhost:11434":
            # Custom endpoint configuration
            ollama.Client(host=self.ollama_endpoint)

    async def validate_connection(self) -> None:
        """Validate Ollama service is accessible.

        Raises:
            ConnectionError: If Ollama service is not available
        """
        try:
            # Attempt to list models as a connectivity check
            ollama.list()
            logger.info(f"Ollama connection validated at {self.ollama_endpoint}")
        except Exception as e:
            error_msg = (
                f"Ollama service not available at {self.ollama_endpoint}. "
                f"Ensure Ollama is running. Error: {e}"
            )
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

    async def validate_model(self, model_name: str) -> None:
        """Validate that the specified model exists in Ollama.

        Args:
            model_name: Name of the model to validate

        Raises:
            ValueError: If model is not found
        """
        try:
            models_response = ollama.list()

            # Handle different response formats
            if isinstance(models_response, dict):
                models_list = models_response.get("models", [])
            else:
                models_list = models_response if isinstance(models_response, list) else []

            # Extract model names, handling both dict and string formats
            available_models = []
            for model in models_list:
                if isinstance(model, dict):
                    available_models.append(model.get("name", model.get("model", "")))
                else:
                    available_models.append(str(model))

            # Check if model exists (handle version suffixes like :latest)
            model_exists = any(
                model_name in model or model.startswith(f"{model_name}:")
                for model in available_models
            )

            if not model_exists:
                error_msg = (
                    f"Model '{model_name}' not found in Ollama. " f"Run: ollama pull {model_name}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f"Model '{model_name}' validated successfully")
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Failed to validate model '{model_name}': {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=30),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate 768-dimensional embedding for text.

        Retries up to 3 times with exponential backoff (1s → 2s → 4s).

        Args:
            text: Input text to embed

        Returns:
            768-dimensional embedding vector

        Raises:
            ConnectionError: If Ollama service unavailable after retries
            ValueError: If response dimension is invalid
            TimeoutError: If request exceeds 30s timeout
        """
        try:
            logger.debug(f"Generating embedding for text (length: {len(text)})")

            # Call Ollama embeddings API
            response = ollama.embeddings(
                model=self.model_name,
                prompt=text,
            )

            # Extract embedding from response
            embedding = response.get("embedding", [])

            # Validate dimension
            if len(embedding) != self.embedding_dim:
                error_msg = (
                    f"Invalid embedding dimension: expected {self.embedding_dim}, "
                    f"got {len(embedding)}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.debug(f"Successfully generated {len(embedding)}-dim embedding")
            return embedding

        except (ConnectionError, TimeoutError):
            # Let tenacity handle retry
            logger.warning("Transient error generating embedding, will retry...")
            raise
        except ValueError:
            # Don't retry validation errors
            raise
        except Exception as e:
            error_msg = f"Failed to generate embedding: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts.

        Processes texts in batches with configurable batch size.
        Uses sequential processing with individual retry logic per embedding.

        Args:
            texts: List of input texts to embed

        Returns:
            List of 768-dimensional embedding vectors

        Raises:
            ConnectionError: If Ollama service unavailable
            ValueError: If any embedding has invalid dimension
        """
        logger.info(f"Generating embeddings for {len(texts)} texts (batch size: {self.batch_size})")

        embeddings = []

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")

            # Generate embeddings sequentially within batch (each has retry logic)
            batch_embeddings = []
            for text in batch:
                embedding = await self.generate_embedding(text)
                batch_embeddings.append(embedding)

            embeddings.extend(batch_embeddings)
            logger.debug(f"Batch {batch_num} completed")

        logger.info(f"Generated {len(embeddings)} embeddings successfully")
        return embeddings
