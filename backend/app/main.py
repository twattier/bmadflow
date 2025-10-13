"""FastAPI application entry point."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import conversations, documents, health, hello, llm_providers, messages, search
from app.config import settings
from app.routers import project_docs, projects
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

app = FastAPI(
    title="BMADFlow API",
    description="Documentation hub for BMAD Method projects",
    version="0.1.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount API routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(hello.router, prefix="/api", tags=["hello"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(llm_providers.router)
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(projects.router)
app.include_router(project_docs.router)


@app.on_event("startup")
async def startup_validation():
    """Validate configuration on backend startup."""
    # GitHub token validation
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.warning(
            "GITHUB_TOKEN not set. GitHub API rate limit: 60 requests/hour. "
            "For production use, create a Personal Access Token at "
            "https://github.com/settings/tokens and add to .env file. "
            "Authenticated rate limit: 5000 requests/hour."
        )
    else:
        logger.info("GitHub API: Authenticated mode (5000 requests/hour)")

    # Ollama validation
    try:
        embedding_service = EmbeddingService(settings.ollama_endpoint_url)
        await embedding_service.validate_connection()
        await embedding_service.validate_model(settings.embedding_model_name)
        logger.info(f"Ollama validation successful: {settings.embedding_model_name}")
    except ConnectionError as e:
        logger.error(f"Ollama not available: {e}")
        raise
    except ValueError as e:
        logger.error(f"Model not found: {e}")
        logger.info(f"Run: ollama pull {settings.embedding_model_name}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "BMADFlow API", "version": "0.1.0"}
