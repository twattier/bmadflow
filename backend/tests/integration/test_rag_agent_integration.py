"""Integration tests for RAG agent pipeline."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.rag_agent import RAGAgent
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.llm_provider import LLMProvider, LLMProviderName
from app.models.project import Project
from app.models.project_doc import ProjectDoc
from app.schemas.agent import RAGResponse, SourceAttribution


@pytest.fixture
async def seeded_project_with_docs(async_db: AsyncSession):
    """Seed database with project, documents, and chunks for testing."""
    # Create project
    project = Project(id=uuid4(), name="Test Project", description="Integration test project")
    async_db.add(project)

    # Create project_doc
    project_doc = ProjectDoc(
        id=uuid4(),
        project_id=project.id,
        doc_type="github",
        source_identifier="test/repo",
        is_active=True,
    )
    async_db.add(project_doc)

    # Create document 1
    doc1 = Document(
        id=uuid4(),
        project_doc_id=project_doc.id,
        file_path="docs/prd.md",
        content="# Product Requirements\n\n## Goals\n\nBuild a documentation hub.",
        file_type="md",
        file_size=100,
        commit_sha="abc123",
    )
    async_db.add(doc1)

    # Create document 2
    doc2 = Document(
        id=uuid4(),
        project_doc_id=project_doc.id,
        file_path="docs/architecture.md",
        content="# Architecture\n\nMonorepo structure with backend and frontend.",
        file_type="md",
        file_size=150,
        commit_sha="abc123",
    )
    async_db.add(doc2)

    # Create chunks with embeddings
    chunk1 = Chunk(
        id=uuid4(),
        document_id=doc1.id,
        chunk_text="Build a documentation hub.",
        chunk_index=0,
        embedding=[0.1] * 768,  # Mock embedding
        header_anchor="goals",
        metadata={"file_path": "docs/prd.md", "file_name": "prd.md", "file_type": "md"},
    )
    async_db.add(chunk1)

    chunk2 = Chunk(
        id=uuid4(),
        document_id=doc2.id,
        chunk_text="Monorepo structure with backend and frontend.",
        chunk_index=0,
        embedding=[0.2] * 768,  # Mock embedding
        header_anchor=None,
        metadata={
            "file_path": "docs/architecture.md",
            "file_name": "architecture.md",
            "file_type": "md",
        },
    )
    async_db.add(chunk2)

    await async_db.commit()
    await async_db.refresh(project)
    await async_db.refresh(project_doc)
    await async_db.refresh(doc1)
    await async_db.refresh(doc2)
    await async_db.refresh(chunk1)
    await async_db.refresh(chunk2)

    return {
        "project": project,
        "project_doc": project_doc,
        "doc1": doc1,
        "doc2": doc2,
        "chunk1": chunk1,
        "chunk2": chunk2,
    }


@pytest.fixture
async def mock_llm_provider(async_db: AsyncSession):
    """Create mock LLM provider in database."""
    provider = LLMProvider(
        id=uuid4(),
        provider_name=LLMProviderName.OLLAMA,
        model_name="llama2",
        is_default=True,
        api_config=None,
    )
    async_db.add(provider)
    await async_db.commit()
    await async_db.refresh(provider)
    return provider


@pytest.mark.asyncio
async def test_rag_agent_full_pipeline(
    async_db: AsyncSession, seeded_project_with_docs, mock_llm_provider
):
    """Test full RAG pipeline with database and mocked LLM."""
    # Arrange
    project = seeded_project_with_docs["project"]
    conversation_id = uuid4()

    agent = RAGAgent(
        project_id=project.id,
        conversation_id=conversation_id,
        llm_provider_id=mock_llm_provider.id,
        top_k=5,
    )

    mock_llm_response = (
        "The project aims to build a documentation hub with a monorepo architecture."
    )

    # Mock LLM service to avoid actual API calls
    with (
        patch("app.agents.rag_agent.LLMService") as mock_llm_service,
        patch("app.agents.tools.vector_search.EmbeddingService") as mock_embed_service,
    ):

        # Mock embedding service
        mock_embed = AsyncMock()
        mock_embed.generate_embedding.return_value = [0.15] * 768
        mock_embed_service.return_value = mock_embed

        # Mock LLM service
        mock_llm = AsyncMock()
        mock_llm.generate_completion.return_value = mock_llm_response
        mock_llm_service.return_value = mock_llm

        # Act
        response = await agent.process_query("What are the project goals?", async_db)

        # Assert
        assert isinstance(response, RAGResponse)
        assert response.response_text == mock_llm_response
        assert len(response.sources) > 0
        assert all(isinstance(s, SourceAttribution) for s in response.sources)

        # Verify sources have correct structure
        source = response.sources[0]
        assert source.document_id is not None
        assert source.file_path in ["docs/prd.md", "docs/architecture.md"]
        assert source.similarity_score >= 0.0
        assert source.similarity_score <= 1.0

        # Verify LLM was called with correct message structure
        mock_llm.generate_completion.assert_called_once()
        call_args = mock_llm.generate_completion.call_args
        messages = call_args[0][1]
        assert any(msg["role"] == "system" for msg in messages)
        assert any(msg["role"] == "user" for msg in messages)
        assert any("What are the project goals?" in msg.get("content", "") for msg in messages)


@pytest.mark.asyncio
async def test_rag_agent_with_header_anchor(
    async_db: AsyncSession, seeded_project_with_docs, mock_llm_provider
):
    """Test RAG agent includes header_anchor in sources."""
    # Arrange
    project = seeded_project_with_docs["project"]
    chunk1 = seeded_project_with_docs["chunk1"]
    conversation_id = uuid4()

    agent = RAGAgent(
        project_id=project.id,
        conversation_id=conversation_id,
        llm_provider_id=mock_llm_provider.id,
        top_k=1,
    )

    mock_llm_response = "Documentation hub."

    with (
        patch("app.agents.rag_agent.LLMService") as mock_llm_service,
        patch("app.agents.tools.vector_search.EmbeddingService") as mock_embed_service,
    ):

        # Mock to return chunk with header_anchor
        mock_embed = AsyncMock()
        mock_embed.generate_embedding.return_value = [0.1] * 768
        mock_embed_service.return_value = mock_embed

        mock_llm = AsyncMock()
        mock_llm.generate_completion.return_value = mock_llm_response
        mock_llm_service.return_value = mock_llm

        # Act
        response = await agent.process_query("goals", async_db)

        # Assert
        assert len(response.sources) > 0
        # Find source with header anchor
        sources_with_anchor = [s for s in response.sources if s.header_anchor]
        assert len(sources_with_anchor) > 0
        assert sources_with_anchor[0].header_anchor == "goals"


@pytest.mark.asyncio
async def test_rag_agent_without_header_anchor(
    async_db: AsyncSession, seeded_project_with_docs, mock_llm_provider
):
    """Test RAG agent handles chunks without header_anchor."""
    # Arrange
    project = seeded_project_with_docs["project"]
    chunk2 = seeded_project_with_docs["chunk2"]
    conversation_id = uuid4()

    agent = RAGAgent(
        project_id=project.id,
        conversation_id=conversation_id,
        llm_provider_id=mock_llm_provider.id,
        top_k=1,
    )

    mock_llm_response = "Monorepo structure."

    with (
        patch("app.agents.rag_agent.LLMService") as mock_llm_service,
        patch("app.agents.tools.vector_search.EmbeddingService") as mock_embed_service,
    ):

        # Mock to return chunk without header_anchor
        mock_embed = AsyncMock()
        mock_embed.generate_embedding.return_value = [0.2] * 768
        mock_embed_service.return_value = mock_embed

        mock_llm = AsyncMock()
        mock_llm.generate_completion.return_value = mock_llm_response
        mock_llm_service.return_value = mock_llm

        # Act
        response = await agent.process_query("architecture", async_db)

        # Assert
        assert len(response.sources) > 0
        # Sources without header_anchor should have None
        sources_without_anchor = [s for s in response.sources if s.header_anchor is None]
        assert len(sources_without_anchor) > 0


@pytest.mark.asyncio
async def test_rag_agent_no_relevant_chunks(
    async_db: AsyncSession, seeded_project_with_docs, mock_llm_provider
):
    """Test RAG agent handles query with no relevant chunks."""
    # Arrange
    project = seeded_project_with_docs["project"]
    conversation_id = uuid4()

    agent = RAGAgent(
        project_id=project.id,
        conversation_id=conversation_id,
        llm_provider_id=mock_llm_provider.id,
        top_k=5,
    )

    with (
        patch("app.agents.tools.vector_search.EmbeddingService") as mock_embed_service,
        patch("app.agents.tools.vector_search.ChunkRepository") as mock_chunk_repo,
    ):

        # Mock embedding service
        mock_embed = AsyncMock()
        mock_embed.generate_embedding.return_value = [0.9] * 768
        mock_embed_service.return_value = mock_embed

        # Mock chunk repository to return no results
        mock_repo = AsyncMock()
        mock_repo.similarity_search.return_value = []
        mock_chunk_repo.return_value = mock_repo

        # Act
        response = await agent.process_query("completely unrelated query", async_db)

        # Assert
        assert isinstance(response, RAGResponse)
        assert "couldn't find" in response.response_text.lower()
        assert len(response.sources) == 0
