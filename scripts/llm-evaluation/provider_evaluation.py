#!/usr/bin/env python3
"""
LLM Provider Evaluation Script
Evaluates OLLAMA (local) and LiteLLM proxy providers for BMAD document extraction.
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import ollama
import platform
from dotenv import load_dotenv
from openai import OpenAI


def get_default_ollama_url() -> str:
    """Get default OLLAMA URL based on environment."""
    # If running in Docker, use container name
    if os.path.exists('/.dockerenv'):
        return "http://ollama:11434"
    # Otherwise use localhost
    return "http://localhost:11434"


@dataclass
class EvaluationConfig:
    """Configuration for provider evaluation."""

    ollama_base_url: str = None
    ollama_extraction_model: str = "qwen2.5:3b"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_embedding_dimension: int = 768

    openai_base_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_extraction_model: Optional[str] = None
    openai_embedding_model: Optional[str] = None
    openai_embedding_dimension: int = 1536

    test_data_dir: Path = Path("test_data")

    @classmethod
    def from_env(cls) -> "EvaluationConfig":
        """Load configuration from environment variables."""
        load_dotenv()

        return cls(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", get_default_ollama_url()),
            ollama_extraction_model=os.getenv("OLLAMA_EXTRACTION_MODEL", "qwen2.5:3b"),
            ollama_embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
            ollama_embedding_dimension=int(os.getenv("OLLAMA_EMBEDDING_DIMENSION", "768")),
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_extraction_model=os.getenv("OPENAI_EXTRACTION_MODEL"),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL"),
            openai_embedding_dimension=int(os.getenv("OPENAI_EMBEDDING_DIMENSION", "1536")),
        )


class OLLAMAProvider:
    """OLLAMA provider for local inference."""

    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.client = ollama.Client(host=config.ollama_base_url)

    def test_connection(self) -> bool:
        """Test connection to OLLAMA server."""
        try:
            response = self.client.list()
            model_names = [m.model for m in response.models]

            # Check if required models are available
            extraction_available = any(self.config.ollama_extraction_model in m for m in model_names)
            embedding_available = any(self.config.ollama_embedding_model in m for m in model_names)

            if not extraction_available:
                print(f"⚠️  Extraction model '{self.config.ollama_extraction_model}' not found")
                print(f"Available models: {', '.join(model_names)}")
                return False

            if not embedding_available:
                print(f"⚠️  Embedding model '{self.config.ollama_embedding_model}' not found")
                print(f"Available models: {', '.join(model_names)}")
                return False

            print(f"✅ OLLAMA connection successful")
            print(f"   Extraction model: {self.config.ollama_extraction_model}")
            print(f"   Embedding model: {self.config.ollama_embedding_model}")
            print(f"   Embedding dimension: {self.config.ollama_embedding_dimension}d")
            return True

        except Exception as e:
            print(f"❌ OLLAMA connection failed: {e}")
            return False

    def extract(self, prompt: str) -> Dict:
        """Extract structured data using OLLAMA."""
        start_time = time.perf_counter()

        try:
            response = self.client.generate(
                model=self.config.ollama_extraction_model,
                prompt=prompt
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            return {
                "success": True,
                "content": response['response'],
                "latency_ms": latency_ms,
                "model": self.config.ollama_extraction_model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "latency_ms": (time.perf_counter() - start_time) * 1000
            }

    def embed(self, text: str) -> Dict:
        """Generate embeddings using OLLAMA."""
        try:
            response = self.client.embeddings(
                model=self.config.ollama_embedding_model,
                prompt=text
            )

            embedding = response['embedding']

            return {
                "success": True,
                "embedding": embedding,
                "dimension": len(embedding),
                "model": self.config.ollama_embedding_model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class LiteLLMProvider:
    """LiteLLM proxy provider for remote inference."""

    def __init__(self, config: EvaluationConfig):
        self.config = config

        if not config.openai_base_url or not config.openai_api_key:
            self.client = None
        else:
            self.client = OpenAI(
                api_key=config.openai_api_key,
                base_url=config.openai_base_url
            )

    def test_connection(self) -> bool:
        """Test connection to LiteLLM proxy."""
        if not self.client:
            print("❌ LiteLLM proxy not configured (missing OPENAI_BASE_URL or OPENAI_API_KEY)")
            return False

        try:
            # Test with a simple completion
            response = self.client.chat.completions.create(
                model=self.config.openai_extraction_model or "gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )

            print(f"✅ LiteLLM proxy connection successful")
            print(f"   Base URL: {self.config.openai_base_url}")
            print(f"   Extraction model: {self.config.openai_extraction_model}")
            print(f"   Embedding model: {self.config.openai_embedding_model}")
            print(f"   Embedding dimension: {self.config.openai_embedding_dimension}d")
            return True

        except Exception as e:
            print(f"❌ LiteLLM proxy connection failed: {e}")
            return False

    def extract(self, prompt: str) -> Dict:
        """Extract structured data using LiteLLM proxy."""
        if not self.client:
            return {"success": False, "error": "LiteLLM proxy not configured"}

        start_time = time.perf_counter()

        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_extraction_model or "gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "latency_ms": latency_ms,
                "model": self.config.openai_extraction_model,
                "tokens": {
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "latency_ms": (time.perf_counter() - start_time) * 1000
            }

    def embed(self, text: str) -> Dict:
        """Generate embeddings using LiteLLM proxy."""
        if not self.client:
            return {"success": False, "error": "LiteLLM proxy not configured"}

        try:
            response = self.client.embeddings.create(
                model=self.config.openai_embedding_model or "text-embedding-ada-002",
                input=text
            )

            embedding = response.data[0].embedding

            return {
                "success": True,
                "embedding": embedding,
                "dimension": len(embedding),
                "model": self.config.openai_embedding_model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """Main entry point for provider evaluation."""
    parser = argparse.ArgumentParser(description="LLM Provider Evaluation")
    parser.add_argument("--test-connection", action="store_true", help="Test provider connections")
    parser.add_argument("--test-data", type=str, default="test_data", help="Test data directory")

    args = parser.parse_args()

    # Load configuration
    config = EvaluationConfig.from_env()
    config.test_data_dir = Path(args.test_data)

    # Initialize providers
    ollama_provider = OLLAMAProvider(config)
    litellm_provider = LiteLLMProvider(config)

    if args.test_connection:
        print("Testing provider connections...\n")

        print("1. OLLAMA Provider:")
        ollama_ok = ollama_provider.test_connection()
        print()

        print("2. LiteLLM Proxy Provider:")
        litellm_ok = litellm_provider.test_connection()
        print()

        if ollama_ok or litellm_ok:
            print("✅ At least one provider is available")
            sys.exit(0)
        else:
            print("❌ No providers available")
            sys.exit(1)

    print("Use --test-connection to verify provider connectivity")
    sys.exit(0)


if __name__ == "__main__":
    main()
