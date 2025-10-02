#!/usr/bin/env python3
"""Simple connectivity test for OLLAMA."""

import os
import ollama
from dotenv import load_dotenv

def test_ollama():
    """Test OLLAMA connection."""
    load_dotenv()

    # Get configuration from environment
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    extraction_model = os.getenv("OLLAMA_EXTRACTION_MODEL", "qwen2.5:3b")
    embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    try:
        # Connect using environment configuration
        client = ollama.Client(host=ollama_url)
        response = client.list()
        model_names = [m.model for m in response.models]

        print(f"✅ OLLAMA connection successful")
        print(f"   URL: {ollama_url}")
        print(f"   Available models: {', '.join(model_names)}")

        # Check for configured models
        extraction_found = any(extraction_model in m for m in model_names)
        embedding_found = any(embedding_model in m for m in model_names)

        print(f"\nConfigured models:")
        print(f"  {extraction_model} - {'✅ Found' if extraction_found else '❌ Not found'}")
        print(f"  {embedding_model} - {'✅ Found' if embedding_found else '❌ Not found'}")

        return extraction_found and embedding_found

    except Exception as e:
        print(f"❌ OLLAMA connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    exit(0 if success else 1)
