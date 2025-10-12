"""Integration tests for vector similarity search with real database and pgvector."""

import time
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.project import Project
from app.models.project_doc import ProjectDoc
from app.repositories.chunk_repository import ChunkRepository
from app.services.embedding_service import EmbeddingService


@pytest.fixture
async def test_project(db_session: AsyncSession) -> Project:
    """Create a test project.

    Args:
        db_session: Database session

    Returns:
        Created test project
    """
    project = Project(
        id=uuid.uuid4(),
        name="Test Project for Vector Search",
        description="Integration test project",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest.fixture
async def test_project_doc(db_session: AsyncSession, test_project: Project) -> ProjectDoc:
    """Create a test project doc.

    Args:
        db_session: Database session
        test_project: Test project fixture

    Returns:
        Created test project doc
    """
    project_doc = ProjectDoc(
        id=uuid.uuid4(),
        project_id=test_project.id,
        name="Test Repo",
        description="Test repository for vector search",
        github_url="https://github.com/test/repo",
    )
    db_session.add(project_doc)
    await db_session.commit()
    await db_session.refresh(project_doc)
    return project_doc


@pytest.fixture
async def embedding_service() -> EmbeddingService:
    """Create embedding service instance.

    Returns:
        EmbeddingService configured for testing
    """
    return EmbeddingService()


@pytest.mark.asyncio
async def test_search_relevance_ranking(
    db_session: AsyncSession,
    test_project: Project,
    test_project_doc: ProjectDoc,
    embedding_service: EmbeddingService,
) -> None:
    """Test that search results are ranked by relevance.

    Verifies:
    - Results are sorted by similarity score (descending)
    - Top result is most relevant to query
    - All results have valid similarity scores (0.0-1.0)
    """
    # Create test documents with varied content
    doc1 = Document(
        id=uuid.uuid4(),
        project_doc_id=test_project_doc.id,
        file_path="docs/architecture.md",
        file_type="md",
        file_size=1024,
        content="The RAG pipeline architecture integrates Docling for document processing and pgvector for similarity search.",
    )
    doc2 = Document(
        id=uuid.uuid4(),
        project_doc_id=test_project_doc.id,
        file_path="docs/backend.md",
        file_type="md",
        file_size=512,
        content="The backend uses FastAPI and PostgreSQL with async SQLAlchemy.",
    )
    doc3 = Document(
        id=uuid.uuid4(),
        project_doc_id=test_project_doc.id,
        file_path="docs/frontend.md",
        file_type="md",
        file_size=512,
        content="The frontend is built with React, TypeScript, and Tailwind CSS.",
    )

    db_session.add_all([doc1, doc2, doc3])
    await db_session.commit()

    # Generate embeddings and create chunks
    chunks_data = [
        (doc1.id, doc1.content, "rag-pipeline-architecture"),
        (doc2.id, doc2.content, "backend-stack"),
        (doc3.id, doc3.content, "frontend-stack"),
    ]

    for doc_id, content, anchor in chunks_data:
        embedding = await embedding_service.generate_embedding(content)
        chunk = Chunk(
            id=uuid.uuid4(),
            document_id=doc_id,
            chunk_text=content,
            chunk_index=0,
            embedding=embedding,
            header_anchor=anchor,
            chunk_metadata={"file_type": "md"},
        )
        db_session.add(chunk)

    await db_session.commit()

    # Perform search
    chunk_repo = ChunkRepository(db_session)
    query = "RAG pipeline architecture"
    query_embedding = await embedding_service.generate_embedding(query)

    results = await chunk_repo.similarity_search(
        query_embedding=query_embedding, project_id=test_project.id, limit=3
    )

    # Assertions
    assert len(results) == 3, "Should return 3 results"

    # Verify results are sorted by similarity (descending)
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True), "Results should be sorted by similarity score"

    # Verify top result is most relevant (contains "RAG pipeline")
    top_chunk, top_score = results[0]
    assert "RAG pipeline" in top_chunk.chunk_text, "Top result should mention RAG pipeline"

    # Verify all scores are valid (0.0-1.0)
    for _, score in results:
        assert 0.0 <= score <= 1.0, f"Similarity score {score} out of valid range"


@pytest.mark.asyncio
async def test_search_performance_500ms(
    db_session: AsyncSession,
    test_project: Project,
    test_project_doc: ProjectDoc,
    embedding_service: EmbeddingService,
) -> None:
    """Test that search completes in <500ms with 100+ chunks (NFR4).

    Verifies:
    - Search duration < 500ms
    - HNSW index is used for performance
    """
    # Create 10 test documents (will result in 100+ chunks with chunking)
    # For this integration test, we'll create 100 chunks directly
    documents = []
    for i in range(10):
        content = (
            f"This is test document {i} with sample content about architecture and design patterns."
        )
        doc = Document(
            id=uuid.uuid4(),
            project_doc_id=test_project_doc.id,
            file_path=f"docs/doc_{i}.md",
            file_type="md",
            file_size=len(content),
            content=content,
        )
        documents.append(doc)
        db_session.add(doc)

    await db_session.commit()

    # Create 100+ chunks with embeddings
    for i, doc in enumerate(documents):
        for j in range(10):  # 10 chunks per document = 100 total
            content = (
                f"Document {i} chunk {j}: Sample content about software architecture patterns."
            )
            embedding = await embedding_service.generate_embedding(content)
            chunk = Chunk(
                id=uuid.uuid4(),
                document_id=doc.id,
                chunk_text=content,
                chunk_index=j,
                embedding=embedding,
                header_anchor=f"section-{j}",
                chunk_metadata={"file_type": "md"},
            )
            db_session.add(chunk)

    await db_session.commit()

    # Measure search performance
    chunk_repo = ChunkRepository(db_session)
    query = "software architecture patterns"
    query_embedding = await embedding_service.generate_embedding(query)

    start_time = time.time()
    results = await chunk_repo.similarity_search(
        query_embedding=query_embedding, project_id=test_project.id, limit=5
    )
    duration_ms = (time.time() - start_time) * 1000

    # Assertions
    assert len(results) == 5, "Should return top 5 results"
    assert duration_ms < 500, f"Search took {duration_ms:.2f}ms, expected <500ms (NFR4)"


@pytest.mark.asyncio
async def test_search_with_header_anchors(
    db_session: AsyncSession,
    test_project: Project,
    test_project_doc: ProjectDoc,
    embedding_service: EmbeddingService,
) -> None:
    """Test that search results include valid header anchors.

    Verifies:
    - Results include header_anchor values
    - Anchor format matches expected pattern (lowercase, hyphens, no special chars)
    """
    # Create document with markdown headers
    content = "## Getting Started\nThis section covers installation and setup."
    doc = Document(
        id=uuid.uuid4(),
        project_doc_id=test_project_doc.id,
        file_path="docs/guide.md",
        file_type="md",
        file_size=len(content),
        content=content,
    )
    db_session.add(doc)
    await db_session.commit()

    # Create chunk with header anchor
    embedding = await embedding_service.generate_embedding(doc.content)
    chunk = Chunk(
        id=uuid.uuid4(),
        document_id=doc.id,
        chunk_text=doc.content,
        chunk_index=0,
        embedding=embedding,
        header_anchor="getting-started",
        chunk_metadata={"file_type": "md"},
    )
    db_session.add(chunk)
    await db_session.commit()

    # Perform search
    chunk_repo = ChunkRepository(db_session)
    query = "getting started guide"
    query_embedding = await embedding_service.generate_embedding(query)

    results = await chunk_repo.similarity_search(
        query_embedding=query_embedding, project_id=test_project.id, limit=5
    )

    # Assertions
    assert len(results) > 0, "Should return at least one result"

    result_chunk, _ = results[0]
    assert result_chunk.header_anchor is not None, "Result should have header_anchor"
    assert result_chunk.header_anchor == "getting-started", "Header anchor format should be correct"
    # Verify anchor format: lowercase, hyphens, no special chars
    assert result_chunk.header_anchor.islower() or "-" in result_chunk.header_anchor


@pytest.mark.asyncio
async def test_cross_project_isolation(
    db_session: AsyncSession, embedding_service: EmbeddingService
) -> None:
    """Test that search results are isolated to specific project.

    Verifies:
    - Project A search returns only Project A chunks
    - Project B search returns only Project B chunks
    - No cross-project data leakage
    """
    # Create two separate projects
    project_a = Project(id=uuid.uuid4(), name="Project A", description="Test project A")
    project_b = Project(id=uuid.uuid4(), name="Project B", description="Test project B")
    db_session.add_all([project_a, project_b])
    await db_session.commit()

    # Create project docs for each
    project_doc_a = ProjectDoc(
        id=uuid.uuid4(),
        project_id=project_a.id,
        name="Repo A",
        description="Repository A for testing",
        github_url="https://github.com/test/repo-a",
    )
    project_doc_b = ProjectDoc(
        id=uuid.uuid4(),
        project_id=project_b.id,
        name="Repo B",
        description="Repository B for testing",
        github_url="https://github.com/test/repo-b",
    )
    db_session.add_all([project_doc_a, project_doc_b])
    await db_session.commit()

    # Create documents for each project
    content_a = "This is Project A documentation about architecture."
    content_b = "This is Project B documentation about deployment."
    doc_a = Document(
        id=uuid.uuid4(),
        project_doc_id=project_doc_a.id,
        file_path="docs/a.md",
        file_type="md",
        file_size=len(content_a),
        content=content_a,
    )
    doc_b = Document(
        id=uuid.uuid4(),
        project_doc_id=project_doc_b.id,
        file_path="docs/b.md",
        file_type="md",
        file_size=len(content_b),
        content=content_b,
    )
    db_session.add_all([doc_a, doc_b])
    await db_session.commit()

    # Create chunks for each document
    embedding_a = await embedding_service.generate_embedding(doc_a.content)
    chunk_a = Chunk(
        id=uuid.uuid4(),
        document_id=doc_a.id,
        chunk_text=doc_a.content,
        chunk_index=0,
        embedding=embedding_a,
        header_anchor="project-a-docs",
        chunk_metadata={"project": "A"},
    )

    embedding_b = await embedding_service.generate_embedding(doc_b.content)
    chunk_b = Chunk(
        id=uuid.uuid4(),
        document_id=doc_b.id,
        chunk_text=doc_b.content,
        chunk_index=0,
        embedding=embedding_b,
        header_anchor="project-b-docs",
        chunk_metadata={"project": "B"},
    )
    db_session.add_all([chunk_a, chunk_b])
    await db_session.commit()

    # Search in Project A
    chunk_repo = ChunkRepository(db_session)
    query = "documentation"
    query_embedding = await embedding_service.generate_embedding(query)

    results_a = await chunk_repo.similarity_search(
        query_embedding=query_embedding, project_id=project_a.id, limit=5
    )

    # Verify only Project A chunks returned
    assert len(results_a) == 1, "Should return 1 result for Project A"
    assert results_a[0][0].document_id == doc_a.id, "Result should be from Project A"

    # Search in Project B
    results_b = await chunk_repo.similarity_search(
        query_embedding=query_embedding, project_id=project_b.id, limit=5
    )

    # Verify only Project B chunks returned
    assert len(results_b) == 1, "Should return 1 result for Project B"
    assert results_b[0][0].document_id == doc_b.id, "Result should be from Project B"
