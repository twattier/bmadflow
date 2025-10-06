# Backend Architecture

> **📖 Implementation Guide**: All code examples in this document follow patterns from [docs/context/backend/fastapi-patterns.md](../context/backend/fastapi-patterns.md) and [docs/context/database/postgresql-pgvector-patterns.md](../context/database/postgresql-pgvector-patterns.md). See [Code Examples Policy](code-examples-policy.md) for mandatory consistency rules.

## Overview

BMADFlow's backend is a **Python 3.11+ FastAPI monolithic REST API** implementing a layered architecture with clear separation between API routes, business logic (service layer), and data access (repository pattern). The backend orchestrates GitHub documentation sync, RAG pipeline processing (Docling + Ollama + pgvector), LLM-powered chatbot interactions, and serves as the single source of truth for all application data.

**Key Architectural Principles:**
- **Layered Architecture**: Routes → Services → Repositories → Database
- **Dependency Injection**: Services and repositories injected into routes
- **Async-First**: SQLAlchemy async engine, async route handlers where beneficial
- **OpenAPI Documentation**: Auto-generated via FastAPI decorators
- **Type Safety**: Pydantic models for request/response validation
- **Testability**: Mockable repositories enable comprehensive unit testing

## Architecture Layers

### 1. API Layer (Routes/Controllers)

**Purpose**: HTTP request handling, input validation, response formatting

**Structure:**
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── projects.py          # Project CRUD endpoints
│   │   │   ├── project_docs.py      # ProjectDoc CRUD + sync endpoints
│   │   │   ├── documents.py         # Document retrieval endpoints
│   │   │   ├── conversations.py     # Chat conversation endpoints
│   │   │   ├── messages.py          # Message send/receive endpoints
│   │   │   ├── llm_providers.py     # LLM configuration endpoints
│   │   │   ├── search.py            # Vector search endpoints
│   │   │   ├── dashboard.py         # Dashboard metrics endpoints
│   │   │   └── health.py            # Health check endpoint
│   │   └── deps.py                  # Dependency injection helpers
```

**Responsibilities:**
- Accept HTTP requests with validation (Pydantic request models)
- Call service layer for business logic
- Return HTTP responses (Pydantic response models)
- Handle HTTP-specific concerns (status codes, headers, CORS)
- OpenAPI/Swagger documentation annotations

**Example Route Pattern:**
```python
@router.post("/projects/{project_id}/docs", response_model=ProjectDocResponse)
async def create_project_doc(
    project_id: UUID,
    request: CreateProjectDocRequest,
    service: ProjectDocService = Depends(get_project_doc_service)
):
    """Create a new ProjectDoc for the specified Project."""
    project_doc = await service.create_project_doc(project_id, request)
    return project_doc
```

---

### 2. Service Layer (Business Logic)

**Purpose**: Core business logic, orchestration, external integrations

**Structure:**
```
backend/
├── app/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── project_service.py        # Project business logic
│   │   ├── project_doc_service.py    # ProjectDoc + sync orchestration
│   │   ├── document_service.py       # Document processing logic
│   │   ├── github_service.py         # GitHub API integration
│   │   ├── rag_service.py            # RAG pipeline orchestration
│   │   ├── embedding_service.py      # Ollama embedding generation
│   │   ├── vector_search_service.py  # pgvector similarity search
│   │   ├── chatbot_service.py        # RAG chatbot + Pydantic agents
│   │   ├── llm_service.py            # LLM provider abstraction
│   │   └── dashboard_service.py      # Dashboard metrics aggregation
```

**Responsibilities:**
- Implement business rules and workflows
- Orchestrate multi-step operations (e.g., sync → process → embed → store)
- Call external APIs (GitHub, Ollama, LLMs)
- Coordinate multiple repositories
- Handle domain-specific errors and retries
- Logging and observability

**Key Services:**

#### ProjectDocService
**Responsibilities:**
- CRUD operations for ProjectDocs
- Sync orchestration: GitHub fetch → document storage → RAG indexing
- Sync status tracking and progress reporting
- Error handling (GitHub rate limits, network failures)

**Key Methods:**
```python
async def sync_project_doc(project_doc_id: UUID) -> SyncResult:
    """
    Orchestrates full sync pipeline:
    1. Fetch GitHub file tree (github_service)
    2. Download file contents (github_service)
    3. Store documents (document_service)
    4. Process and embed (rag_service)
    5. Update last_synced_at timestamp
    """
    pass
```

#### RAGService
**Responsibilities:**
- Document processing pipeline (Docling integration)
- Embedding generation coordination (embedding_service)
- Vector storage management (vector_search_service)
- Header anchor extraction during chunking

**Key Methods:**
```python
async def process_and_index_document(document_id: UUID) -> IndexResult:
    """
    Process document through RAG pipeline:
    1. Load document content from DB
    2. Process with Docling HybridChunker
    3. Extract header anchors from chunks
    4. Generate embeddings via Ollama
    5. Store in pgvector with metadata
    """
    pass
```

#### ChatbotService
**Responsibilities:**
- RAG query processing (query → vector search → LLM generation)
- Pydantic agent orchestration
- Source attribution formatting
- Conversation history management

**Key Methods:**
```python
async def generate_rag_response(
    project_id: UUID,
    conversation_id: UUID,
    user_message: str,
    llm_provider_id: UUID
) -> RAGResponse:
    """
    Generate RAG-powered response:
    1. Generate query embedding
    2. Perform vector similarity search (scoped to project)
    3. Retrieve top-k chunks with metadata
    4. Format context for LLM
    5. Call LLM provider for generation
    6. Parse sources from response
    7. Return response + source attribution
    """
    pass
```

#### LLMService
**Responsibilities:**
- Abstraction over multiple LLM providers (OpenAI, Google, LiteLLM, Ollama)
- Provider-specific API client management
- Error handling and retries
- Response streaming (optional)

**Supported Providers:**
```python
class LLMProvider(enum.Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    LITELLM = "litellm"
    OLLAMA = "ollama"

async def generate_completion(
    provider: LLMProvider,
    model: str,
    messages: List[Message],
    config: dict
) -> CompletionResponse:
    """Route to appropriate provider client."""
    pass
```

---

### 3. Repository Layer (Data Access)

**Purpose**: Database abstraction, query optimization, ORM operations

**Structure:**
```
backend/
├── app/
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── project_repository.py
│   │   ├── project_doc_repository.py
│   │   ├── document_repository.py
│   │   ├── chunk_repository.py
│   │   ├── conversation_repository.py
│   │   ├── message_repository.py
│   │   ├── llm_provider_repository.py
│   │   └── base_repository.py         # Generic CRUD operations
```

**Responsibilities:**
- Execute database queries (SQLAlchemy ORM)
- Optimize query performance (joins, indexes, eager loading)
- Transaction management
- Database error handling

**Example Repository Pattern:**
```python
class ProjectDocRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_doc_id: UUID) -> Optional[ProjectDoc]:
        """Retrieve ProjectDoc by ID with eager loading of relationships."""
        pass

    async def list_by_project(self, project_id: UUID) -> List[ProjectDoc]:
        """List all ProjectDocs for a Project."""
        pass

    async def update_sync_timestamp(self, project_doc_id: UUID, timestamp: datetime):
        """Update last_synced_at after successful sync."""
        pass
```

**Vector Search Repository:**
```python
class ChunkRepository:
    async def similarity_search(
        self,
        query_embedding: List[float],
        project_id: UUID,
        top_k: int = 5
    ) -> List[ChunkWithScore]:
        """
        Perform pgvector cosine similarity search:
        SELECT id, chunk_text, metadata, header_anchor, document_id,
               1 - (embedding <=> :query_embedding) as similarity_score
        FROM chunks
        WHERE project_id = :project_id
        ORDER BY embedding <=> :query_embedding
        LIMIT :top_k
        """
        pass
```

---

### 4. Model Layer (Data Models)

**Purpose**: Define database schema (SQLAlchemy ORM) and API contracts (Pydantic DTOs)

**Structure:**
```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── project.py              # SQLAlchemy ORM models
│   │   ├── project_doc.py
│   │   ├── document.py
│   │   ├── chunk.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── llm_provider.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── project.py              # Pydantic request/response DTOs
│   │   ├── project_doc.py
│   │   ├── document.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── llm_provider.py
│   │   └── common.py               # Shared DTOs (pagination, errors)
```

**SQLAlchemy ORM Models:**
- Map to PostgreSQL tables
- Define relationships (Foreign Keys, lazy/eager loading)
- Include pgvector column type for embeddings
- Timestamps (created_at, updated_at) via mixins

**Pydantic Schemas:**
- Request validation (POST/PUT bodies)
- Response serialization (API responses)
- Type safety for frontend integration
- OpenAPI schema generation

**Example ORM Model:**
```python
class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector(768), nullable=False)  # pgvector type
    header_anchor = Column(String(512), nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")
```

---

## RAG Pipeline Implementation

### Pipeline Overview

```mermaid
graph LR
    A[Document Synced] --> B[Docling Processing]
    B --> C[HybridChunker]
    C --> D[Extract Header Anchors]
    D --> E[Generate Embeddings<br/>Ollama API]
    E --> F[Store in pgvector<br/>with Metadata]
    F --> G[Indexed & Searchable]
```

### Docling Integration

**Library**: `docling` (Python package)

**Processing Strategy**: HybridChunker with default settings

**Supported File Types:**
- Markdown (.md) - Primary use case
- CSV (.csv) - Row-based chunking
- YAML/JSON (.yaml, .yml, .json) - Structure-aware chunking
- TXT (.txt) - Plain text chunking

**Chunking Configuration:**
```python
from docling import DocumentProcessor
from docling.chunking import HybridChunker

processor = DocumentProcessor()
chunker = HybridChunker()  # Default settings (no custom config for POC)

def process_document(content: str, file_type: str) -> List[Chunk]:
    """Process document content into optimized chunks."""
    doc = processor.load_from_text(content, file_type=file_type)
    chunks = chunker.chunk(doc)
    return chunks
```

**Header Anchor Extraction:**
```python
def extract_header_anchor(chunk: Chunk, full_document: str) -> Optional[str]:
    """
    Extract nearest preceding header for markdown chunks.
    Converts header text to anchor format: lowercase, hyphens, no special chars.
    Returns None if no header identifiable.
    """
    # Implementation: Parse markdown AST, find nearest H1-H3 before chunk position
    # Convert header text to anchor: "## Database Schema" → "database-schema"
    pass
```

### Ollama Embedding Generation

**Client Library**: `ollama-python`

**Model**: nomic-embed-text (dimension 768) - **FIXED for POC**

**Configuration:**
```python
import ollama

OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT_URL", "http://localhost:11434")
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIM = 768

async def generate_embedding(text: str) -> List[float]:
    """Generate 768-dim embedding using Ollama."""
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )
    embedding = response["embedding"]
    assert len(embedding) == EMBEDDING_DIM, "Unexpected embedding dimension"
    return embedding
```

**Batch Processing:**
```python
async def generate_embeddings_batch(texts: List[str], batch_size: int = 10) -> List[List[float]]:
    """Generate embeddings in batches to optimize Ollama throughput."""
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = await asyncio.gather(*[generate_embedding(text) for text in batch])
        embeddings.extend(batch_embeddings)
    return embeddings
```

**Startup Validation:**
```python
async def validate_ollama_setup():
    """Validate Ollama availability and model on backend startup."""
    try:
        # Check Ollama connectivity
        response = ollama.list()
        models = [m["name"] for m in response["models"]]

        if EMBEDDING_MODEL not in models:
            raise RuntimeError(
                f"Ollama model '{EMBEDDING_MODEL}' not found. "
                f"Run: ollama pull {EMBEDDING_MODEL}"
            )

        # Test embedding generation
        test_embedding = await generate_embedding("test")
        assert len(test_embedding) == EMBEDDING_DIM

        logger.info(f"Ollama setup validated: {EMBEDDING_MODEL} ready")
    except Exception as e:
        logger.error(f"Ollama validation failed: {e}")
        raise
```

### Vector Search Implementation

**Query Flow:**
1. User submits chat query
2. Generate query embedding via Ollama
3. Perform pgvector cosine similarity search (filtered by project_id)
4. Retrieve top-k chunks with metadata (document_id, file_path, header_anchor, similarity_score)
5. Pass chunks as context to LLM

**SQL Query (via SQLAlchemy):**
```python
async def similarity_search(
    query_embedding: List[float],
    project_id: UUID,
    top_k: int = 5,
    similarity_threshold: float = 0.7
) -> List[ChunkResult]:
    """Perform pgvector similarity search with cosine distance."""

    # pgvector operator: <=> (cosine distance)
    # Convert to similarity score: 1 - distance
    query = select(
        Chunk.id,
        Chunk.chunk_text,
        Chunk.header_anchor,
        Chunk.metadata,
        Chunk.document_id,
        Document.file_path,
        (1 - Chunk.embedding.cosine_distance(query_embedding)).label("similarity_score")
    ).join(
        Document, Chunk.document_id == Document.id
    ).join(
        ProjectDoc, Document.project_doc_id == ProjectDoc.id
    ).where(
        ProjectDoc.project_id == project_id,
        (1 - Chunk.embedding.cosine_distance(query_embedding)) >= similarity_threshold
    ).order_by(
        Chunk.embedding.cosine_distance(query_embedding)
    ).limit(top_k)

    result = await db.execute(query)
    return result.all()
```

**Performance Target**: <500ms per search (NFR4)

**Optimization Strategies:**
- HNSW index on embedding column (created via Alembic migration)
- Project-scoped queries to reduce search space
- Configurable top_k (default 5) and similarity_threshold (default 0.7)
- Connection pooling (SQLAlchemy async engine)

---

## Pydantic Agent Framework

### Agent Architecture

**Purpose**: Structured RAG agents using Pydantic for type safety and tool definitions

**Framework**: Pydantic v2+ (not LangChain - per PRD requirement FR28)

**Agent Structure:**
```
backend/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Abstract agent base class
│   │   ├── rag_agent.py           # RAG chatbot agent
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── vector_search.py   # Vector search tool
│   │   │   ├── get_document.py    # Document retrieval tool
│   │   │   └── format_sources.py  # Source attribution tool
│   │   └── prompts/
│   │       ├── __init__.py
│   │       └── rag_system_prompt.py
```

### RAG Agent Implementation

**Agent Definition:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class VectorSearchTool(BaseModel):
    """Tool for retrieving relevant document chunks."""

    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=5, description="Number of results to return")

    async def execute(self, project_id: UUID, vector_search_service) -> List[ChunkResult]:
        """Execute vector similarity search."""
        query_embedding = await vector_search_service.generate_query_embedding(self.query)
        results = await vector_search_service.search(query_embedding, project_id, self.top_k)
        return results


class RAGAgent(BaseModel):
    """RAG chatbot agent with tool access."""

    project_id: UUID
    conversation_id: UUID
    llm_provider_id: UUID

    tools: List[BaseModel] = Field(default_factory=lambda: [VectorSearchTool])

    async def process_query(self, user_message: str) -> RAGResponse:
        """
        Process user query with RAG pipeline:
        1. Use VectorSearchTool to retrieve relevant chunks
        2. Format chunks as context for LLM
        3. Call LLM with system prompt + context + user message
        4. Parse response and extract sources
        5. Return structured response with source attribution
        """

        # Step 1: Vector search
        search_tool = VectorSearchTool(query=user_message, top_k=5)
        chunks = await search_tool.execute(self.project_id, vector_search_service)

        # Step 2: Format context
        context = self._format_context(chunks)

        # Step 3: Generate LLM response
        messages = [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_message}"}
        ]

        llm_response = await llm_service.generate_completion(
            provider_id=self.llm_provider_id,
            messages=messages
        )

        # Step 4: Format sources
        sources = self._format_sources(chunks)

        return RAGResponse(
            response_text=llm_response.content,
            sources=sources
        )

    def _format_context(self, chunks: List[ChunkResult]) -> str:
        """Format chunks as context for LLM prompt."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            anchor = f"#{chunk.header_anchor}" if chunk.header_anchor else ""
            context_parts.append(
                f"[Source {i}: {chunk.file_path}{anchor}]\n{chunk.chunk_text}\n"
            )
        return "\n".join(context_parts)

    def _format_sources(self, chunks: List[ChunkResult]) -> List[SourceAttribution]:
        """Format source attribution for frontend display."""
        return [
            SourceAttribution(
                document_id=chunk.document_id,
                file_path=chunk.file_path,
                header_anchor=chunk.header_anchor,
                similarity_score=chunk.similarity_score
            )
            for chunk in chunks
        ]
```

**System Prompt:**
```python
RAG_SYSTEM_PROMPT = """You are a helpful AI assistant for BMADFlow, a documentation hub for BMAD Method projects.

Your role is to answer questions based ONLY on the provided context from project documentation. If the context doesn't contain enough information to answer the question, say so clearly.

When answering:
- Cite sources using the [Source N] references provided
- Be concise and direct
- Focus on technical accuracy
- If multiple sources conflict, acknowledge the discrepancy

Do not:
- Make up information not in the context
- Assume details not explicitly stated
- Answer questions outside the scope of the provided documentation
"""
```

---

## Background Jobs & Async Processing

### Sync Operations

**Challenge**: Document sync operations are long-running (target: <5min per ProjectDoc per NFR3)

**Solution**: Async processing with progress tracking

**Approach Options:**

#### Option 1: FastAPI Background Tasks (Recommended for POC)
```python
from fastapi import BackgroundTasks

@router.post("/project-docs/{id}/sync")
async def trigger_sync(
    id: UUID,
    background_tasks: BackgroundTasks,
    service: ProjectDocService = Depends()
):
    """Trigger async sync operation."""
    background_tasks.add_task(service.sync_project_doc, id)
    return {"status": "sync_started", "project_doc_id": id}
```

**Pros**: Simple, no additional infrastructure
**Cons**: No retry logic, limited observability

#### Option 2: Celery Workers (Future Enhancement)
```python
from celery import Celery

celery_app = Celery("bmadflow", broker="redis://localhost:6379")

@celery_app.task(bind=True, max_retries=3)
def sync_project_doc_task(self, project_doc_id: str):
    """Celery task for sync with retry logic."""
    try:
        # Sync logic
        pass
    except Exception as e:
        self.retry(exc=e, countdown=60)
```

**Pros**: Retry logic, distributed processing, better observability
**Cons**: Additional infrastructure (Redis/RabbitMQ), complexity

**POC Decision**: Use FastAPI BackgroundTasks for simplicity. Document Celery upgrade path for production.

---

## Error Handling Patterns

### GitHub API Errors

**Rate Limiting:**
```python
class GitHubService:
    async def fetch_with_retry(self, url: str, max_retries: int = 3):
        """Fetch GitHub API with rate limit handling."""
        for attempt in range(max_retries):
            try:
                response = await self.client.get(url)

                # Check rate limit headers
                remaining = int(response.headers.get("X-RateLimit-Remaining", 999))
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))

                if remaining < 5:
                    wait_seconds = reset_time - time.time()
                    logger.warning(f"GitHub rate limit approaching. Waiting {wait_seconds}s")
                    await asyncio.sleep(wait_seconds)

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:  # Rate limit exceeded
                    reset_time = int(e.response.headers.get("X-RateLimit-Reset", 0))
                    wait_seconds = reset_time - time.time()
                    raise RateLimitExceededError(
                        f"GitHub rate limit exceeded. Reset at {datetime.fromtimestamp(reset_time)}"
                    )
                raise
```

### Ollama Connection Errors

**Retry Logic:**
```python
class EmbeddingService:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.RequestError)
    )
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding with retry on transient Ollama errors."""
        try:
            return await ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            raise
```

### LLM Provider Errors

**Provider Fallback:**
```python
class LLMService:
    async def generate_with_fallback(
        self,
        messages: List[Message],
        primary_provider_id: UUID
    ) -> CompletionResponse:
        """Try primary provider, fallback to default if fails."""
        try:
            return await self.generate_completion(primary_provider_id, messages)
        except LLMProviderError as e:
            logger.warning(f"Primary LLM provider failed: {e}. Trying default.")
            default_provider = await self.get_default_provider()
            return await self.generate_completion(default_provider.id, messages)
```

---

## API Conventions

### REST Endpoint Patterns

**Resource Naming:**
- Plural nouns: `/api/projects`, `/api/conversations`
- Nested resources: `/api/projects/{id}/docs`, `/api/conversations/{id}/messages`
- Actions as POST to resource: `/api/project-docs/{id}/sync`

**HTTP Methods:**
- `GET` - Retrieve resource(s)
- `POST` - Create resource or trigger action
- `PUT` - Update entire resource
- `PATCH` - Partial update (not used in POC)
- `DELETE` - Remove resource

**Response Codes:**
- `200 OK` - Successful GET/PUT/DELETE
- `201 Created` - Successful POST creating resource
- `202 Accepted` - Async operation started (sync endpoint)
- `400 Bad Request` - Validation error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Request/Response Standards

**Request Bodies**: Pydantic schemas with validation
```python
class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)
```

**Response Bodies**: Pydantic schemas serialized to JSON
```python
class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
```

**Error Responses**: Standardized format
```python
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str]
    status_code: int

# Example
{
    "error": "Project not found",
    "detail": "No project exists with ID: 123e4567-e89b-12d3-a456-426614174000",
    "status_code": 404
}
```

### Pagination

**List Endpoints:**
```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool

@router.get("/projects", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(page: int = 1, page_size: int = 20):
    """List projects with pagination."""
    pass
```

---

## Configuration Management

### Environment Variables

**Configuration File**: `.env` (loaded via `python-dotenv`)

**Required Variables:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/bmadflow
POSTGRES_USER=bmadflow
POSTGRES_PASSWORD=changeme
POSTGRES_DB=bmadflow

# Ports
BACKEND_PORT=8000
POSTGRES_PORT=5432

# Ollama
OLLAMA_ENDPOINT_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text

# LLM Providers (Optional)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
LITELLM_CONFIG=...

# GitHub (Optional - increases rate limit)
GITHUB_TOKEN=ghp_...

# Application
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

**Configuration Loading:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    backend_port: int = 8000
    ollama_endpoint_url: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text"
    openai_api_key: Optional[str] = None
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Related Documentation

- **Database Schema**: [database-schema.md](database-schema.md)
- **Data Models**: [data-models.md](data-models.md)
- **API Specification**: [api-specification.md](api-specification.md)
- **FastAPI Patterns**: [/docs/context/backend/fastapi-patterns.md](../context/backend/fastapi-patterns.md)
- **PostgreSQL+pgvector Patterns**: [/docs/context/database/postgresql-pgvector-patterns.md](../context/database/postgresql-pgvector-patterns.md)

---
