"""Seed script for LLM providers.

Creates default Ollama qwen2.5:7b-instruct-q4_K_M provider if no default exists.

Usage:
    python scripts/seed_llm_providers.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))


from app.database import AsyncSessionLocal
from app.models.llm_provider import LLMProviderName
from app.repositories.llm_provider_repository import LLMProviderRepository
from app.schemas.llm_provider import LLMProviderCreate

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def seed_default_provider():
    """Seed default Ollama qwen2.5:7b-instruct-q4_K_M provider if no default exists."""
    async with AsyncSessionLocal() as db:
        async with db.begin():
            repo = LLMProviderRepository(db)

            # Check if default provider exists
            default_provider = await repo.get_default()

            if default_provider:
                logger.info(
                    f"Default provider already exists: {default_provider.provider_name} "
                    f"/ {default_provider.model_name}"
                )
                return

            # Create default Ollama qwen2.5:7b-instruct-q4_K_M provider
            logger.info(
                "No default provider found. Creating Ollama qwen2.5:7b-instruct-q4_K_M provider..."
            )

            provider_data = LLMProviderCreate(
                provider_name=LLMProviderName.OLLAMA,
                model_name="qwen2.5:7b-instruct-q4_K_M",
                is_default=True,
                api_config={"api_base": "http://localhost:11434"},
            )

            provider = await repo.create(provider_data)

            logger.info(
                f"Default provider created: {provider.provider_name} / {provider.model_name} "
                f"(ID: {provider.id})"
            )


async def main():
    """Main entry point."""
    try:
        logger.info("Starting LLM provider seeding...")
        await seed_default_provider()
        logger.info("Seeding complete!")
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
