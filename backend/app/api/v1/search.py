"""Search API endpoints for vector similarity search."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_chunk_repository, get_db, get_embedding_service
from app.repositories.chunk_repository import ChunkRepository
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/projects/{project_id}/search",
    response_model=SearchResponse,
    summary="Perform vector similarity search",
    description=(
        "Search for relevant chunks using semantic similarity (pgvector + nomic-embed-text). "
        "Results are scoped to the specified project for data isolation."
    ),
    responses={
        200: {
            "description": "Search completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "query": "How does the RAG pipeline work?",
                        "results": [
                            {
                                "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
                                "document_id": "660e8400-e29b-41d4-a716-446655440000",
                                "chunk_text": "The RAG pipeline integrates Docling...",
                                "similarity_score": 0.89,
                                "header_anchor": "rag-pipeline",
                                "metadata": {
                                    "file_path": "docs/architecture.md",
                                    "file_name": "architecture.md",
                                    "file_type": "md",
                                },
                            }
                        ],
                        "total_results": 1,
                    }
                }
            },
        },
        404: {"description": "Project not found"},
        422: {"description": "Validation error (invalid top_k or empty query)"},
        500: {"description": "Internal server error (Ollama unavailable, database error)"},
    },
)
async def search_embeddings(
    project_id: UUID,
    request: SearchRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    chunk_repo: ChunkRepository = Depends(get_chunk_repository),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """Perform vector similarity search scoped to project.

    Args:
        project_id: UUID of the project to search within
        request: Search request with query text and top_k parameter
        embedding_service: Service for generating query embeddings
        chunk_repo: Repository for chunk database operations
        db: Database session

    Returns:
        SearchResponse with top-k relevant chunks and similarity scores

    Raises:
        HTTPException: 404 if project not found, 500 if search fails
    """
    try:
        logger.info(
            f"Search query: '{request.query}' (top_k={request.top_k}, project_id={project_id})"
        )

        # Generate query embedding
        query_embedding = await embedding_service.generate_embedding(request.query)
        logger.debug(f"Generated query embedding: dimension={len(query_embedding)}")

        # Perform vector similarity search
        results = await chunk_repo.similarity_search(
            query_embedding=query_embedding, project_id=project_id, limit=request.top_k
        )

        # Build SearchResult objects from chunk results
        search_results = [
            SearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                chunk_text=chunk.chunk_text,
                similarity_score=score,
                header_anchor=chunk.header_anchor,
                metadata=chunk.chunk_metadata or {},
            )
            for chunk, score in results
        ]

        logger.info(
            f"Search completed: {len(search_results)} results returned for query '{request.query}'"
        )

        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
        )

    except ValueError as e:
        # Validation errors (e.g., invalid limit)
        logger.error(f"Validation error in search: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except ConnectionError as e:
        # Ollama service unavailable
        logger.error(f"Ollama service error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Embedding service unavailable. Ensure Ollama is running.",
        )
    except Exception as e:
        # Database or other errors
        logger.error(f"Vector search failed for project {project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed")
