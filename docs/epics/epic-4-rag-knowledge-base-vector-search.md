# Epic 4: RAG Knowledge Base & Vector Search

## Epic Goal

Implement the RAG infrastructure using Docling for document processing, Ollama for embeddings, pgvector for storage, and build vector similarity search to power the AI chatbot.

## Pre-Development Checklist

**Complete these tasks before starting Story 4.1:**

### Critical Dependencies
- [ ] **Install Backend Libraries**
  ```bash
  cd backend
  pip install docling ollama-python
  # Verify installation
  python -c "import docling; import ollama; print('Dependencies OK')"
  ```
- [ ] **Verify Ollama Setup**
  ```bash
  ollama list | grep nomic-embed-text
  # If not found, run:
  ollama pull nomic-embed-text
  ```
- [ ] **Enable pgvector Extension**
  ```bash
  # Connect to PostgreSQL
  psql -h localhost -U postgres -d bmadflow
  # Run in psql:
  CREATE EXTENSION IF NOT EXISTS vector;
  # Verify:
  SELECT * FROM pg_extension WHERE extname = 'vector';
  ```

### Validation
- [ ] Review Epic 3 completion status (all P0 stories done)
- [ ] Confirm documents table populated with content (from Epic 2)
- [ ] Review [docs/architecture/backend-architecture.md](../architecture/backend-architecture.md)
- [ ] Review [docs/architecture/database-schema.md](../architecture/database-schema.md)

---

## Epic Status

**STATUS:** 📋 **READY FOR DEVELOPMENT** - Pre-development validation complete

All prerequisites met:
- Epic 3 complete (Documentation Explorer functional)
- Documents table populated with file content
- Tech stack validated (Docling, Ollama, pgvector)

**Story Sequencing:** Sequential execution required (4.1 → 4.2 → 4.3 → 4.4 → 4.5 → 4.6)

---

## Story Sequencing & Dependencies

### Critical Path (Sequential) - Must Complete in Order
```
Story 4.1 (Docling Integration)
    ↓
Story 4.2 (Ollama Embeddings)
    ↓
Story 4.3 (Vector DB Schema)
    ↓
Story 4.4 (Header Anchors)
    ↓
Story 4.5 (Sync Pipeline)
    ↓
Story 4.6 (Vector Search API)
```

### Dependency Summary
| Story | Depends On | Blocks | Priority |
|-------|------------|--------|----------|
| 4.1 | Epic 2 (documents table) | 4.2, 4.3, 4.4, 4.5 | P0 |
| 4.2 | Story 4.1 (chunk data) | 4.3, 4.5, 4.6 | P0 |
| 4.3 | Story 4.2 (embeddings) | 4.5, 4.6 | P0 |
| 4.4 | Story 4.1 (chunk data) | 4.5 | P0 |
| 4.5 | Stories 4.1, 4.2, 4.3, 4.4 | Epic 5 (Chatbot) | P0 |
| 4.6 | Stories 4.2, 4.3, 4.5 | Epic 5 (Chatbot) | P0 |

---

## Architecture Context

### Database Schema - Existing Tables

**Current Schema** (from Epic 2):
```python
# Existing tables that Epic 4 will reference
class Project(Base):
    __tablename__ = "projects"
    id: Mapped[uuid.UUID]
    name: Mapped[str]
    # ... other fields

class ProjectDoc(Base):
    __tablename__ = "project_docs"
    id: Mapped[uuid.UUID]
    project_id: Mapped[uuid.UUID]  # FK to projects
    # ... other fields

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID]
    project_doc_id: Mapped[uuid.UUID]  # FK to project_docs
    file_path: Mapped[str]
    file_type: Mapped[str]
    file_size: Mapped[int]
    content: Mapped[str]  # Full file content (Story 4.1 will chunk this)
    metadata: Mapped[dict | None]
    # ... other fields
```

**New Table (Story 4.3):**
```python
class Embedding(Base):
    __tablename__ = "embeddings"
    id: Mapped[uuid.UUID]
    project_id: Mapped[uuid.UUID]  # FK to projects (for filtering)
    project_doc_id: Mapped[uuid.UUID]  # FK to project_docs
    document_id: Mapped[uuid.UUID]  # FK to documents
    chunk_text: Mapped[str]
    chunk_index: Mapped[int]
    embedding: Mapped[Vector]  # pgvector type, dim=768
    header_anchor: Mapped[str | None]  # Story 4.4
    metadata: Mapped[dict]  # file_path, file_name, file_type, etc.
    created_at: Mapped[datetime]
```

### Service Layer Architecture

**New Services (Epic 4):**
- `DoclingService` (`app/services/docling_service.py`) - Story 4.1
- `EmbeddingService` (`app/services/embedding_service.py`) - Story 4.2
- `EmbeddingRepository` (`app/repositories/embedding_repository.py`) - Story 4.3

**Dependency Injection Pattern:**
```python
# app/api/deps.py
async def get_docling_service() -> DoclingService:
    return DoclingService()

async def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(ollama_endpoint=settings.OLLAMA_ENDPOINT_URL)
```

### Code Quality Standards (All Stories)

**Required for Every Story:**
1. **Formatting**: `black app/ tests/` (line length 100)
2. **Linting**: `ruff check app/ tests/ --fix`
3. **Type Hints**: All functions with `List`, `Dict`, `Optional`, `UUID`
4. **Docstrings**: Google style for public functions
5. **Logging**: `logger.info()` for operations, `logger.error()` for failures
6. **Tests**: Unit + Integration, 70%+ coverage (per NFR18)

---

## Stories

### Story 4.1: Integrate Docling Library and Document Processing Pipeline

**Story File:** [4.1-integrate-docling-document-processing.md](../stories/4.1-integrate-docling-document-processing.md) *(to be created by SM)*

**As a** developer,
**I want** to process synced documents using Docling's HybridChunker,
**so that** I can generate optimized chunks for RAG.

**Acceptance Criteria:**
1. Docling library integrated into backend (`requirements.txt`: `docling>=1.0.0`)
2. `DoclingService` created in `app/services/docling_service.py` using HybridChunker
3. Method `process_markdown(content: str) -> List[Chunk]`: serialize, chunk, extract metadata
4. Method `process_csv(content: str) -> List[Chunk]`: serialize, chunk by rows
5. Method `process_yaml_json(content: str, file_type: str) -> List[Chunk]`: chunk by structure
6. Chunk size configured: Docling defaults (typically 512 tokens for technical docs)
7. Unit tests: 5+ tests in `tests/unit/services/test_docling_service.py`
8. Integration test: `tests/integration/test_document_processing.py` - process 10+ BMAD files

**Implementation Notes:**
- **Service Location**: `backend/app/services/docling_service.py`
- **Schema Location**: `backend/app/schemas/chunk.py` (create `ChunkResponse` model)
- **Chunk Model**:
  ```python
  class Chunk(BaseModel):
      text: str
      index: int
      metadata: dict  # Contains: file_path, file_type, position, total_chunks
  ```
- **Error Handling**: Raise `ValueError` for unsupported file types, log errors with `logger.error()`
- **Dependencies**: `from docling.chunking import HybridChunker`

**Testing Requirements:**
- **Unit Tests** (`tests/unit/services/test_docling_service.py`):
  - `test_process_markdown_simple` - Basic markdown with headers
  - `test_process_markdown_code_blocks` - Code fence handling
  - `test_process_csv_with_headers` - CSV with header row
  - `test_process_yaml_structure` - Nested YAML chunking
  - `test_process_json_structure` - JSON array/object chunking
  - `test_unsupported_file_type` - Raises ValueError
  - **Coverage Target**: 80%+ for DoclingService

- **Integration Tests** (`tests/integration/test_document_processing.py`):
  - `test_process_bmad_prd_markdown` - Process actual PRD.md
  - `test_process_multiple_file_types` - Mix of MD, CSV, YAML
  - `test_chunk_metadata_complete` - Verify all metadata fields
  - **Coverage Target**: 70%+ overall

**Code Quality Checklist:**
- [ ] Black formatting applied
- [ ] Ruff linting passed (no errors)
- [ ] Type hints on all functions
- [ ] Google-style docstrings
- [ ] Structured logging for chunk counts
- [ ] Error messages clear and actionable

---

### Story 4.2: Implement Ollama Embedding Generation

**Story File:** [4.2-implement-ollama-embedding-generation.md](../stories/4.2-implement-ollama-embedding-generation.md) *(to be created by SM)*

**As a** developer,
**I want** to generate embeddings using Ollama with nomic-embed-text model,
**so that** I can create vector representations of document chunks.

**Acceptance Criteria:**
1. Ollama client library integrated (`requirements.txt`: `ollama>=0.1.0`)
2. Environment variable `OLLAMA_ENDPOINT_URL` configured in `.env` (default: `http://localhost:11434`)
3. Backend validates Ollama connectivity on startup, raises `ConnectionError` with message if unavailable
4. Backend validates `nomic-embed-text` model, raises `ValueError` with install instructions if missing
5. Method `generate_embedding(text: str) -> List[float]`: returns 768-dim vector
6. Method `generate_embeddings_batch(texts: List[str]) -> List[List[float]]`: batch processing (10 chunks/batch)
7. Error handling: Retry 3 times with exponential backoff (1s→2s→4s), max timeout 30s per request
8. Unit tests: 6+ tests in `tests/unit/services/test_embedding_service.py` with mocked Ollama
9. Integration test: `tests/integration/test_ollama_embedding.py` - real Ollama, verify 768 dims

**Implementation Notes:**
- **Service Location**: `backend/app/services/embedding_service.py`
- **Config Location**: `backend/app/config.py` (add `OLLAMA_ENDPOINT_URL` to Settings class)
- **Startup Validation** (`app/main.py`):
  ```python
  @app.on_event("startup")
  async def validate_ollama():
      try:
          embedding_service = EmbeddingService(settings.OLLAMA_ENDPOINT_URL)
          await embedding_service.validate_connection()
          await embedding_service.validate_model("nomic-embed-text")
      except ConnectionError as e:
          logger.error(f"Ollama not available: {e}")
          raise
      except ValueError as e:
          logger.error(f"Model not found: {e}")
          logger.info("Run: ollama pull nomic-embed-text")
          raise
  ```
- **Retry Logic**:
  ```python
  from tenacity import retry, stop_after_attempt, wait_exponential

  @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=30))
  async def _call_ollama(self, text: str) -> List[float]:
      # Ollama API call here
  ```
- **Batch Size**: 10 chunks per batch (configurable via `EMBEDDING_BATCH_SIZE` env var)

**Testing Requirements:**
- **Unit Tests** (`tests/unit/services/test_embedding_service.py`):
  - `test_generate_embedding_success` - Mock Ollama returns 768-dim vector
  - `test_generate_embedding_invalid_response` - Mock returns wrong dimension
  - `test_generate_embeddings_batch` - Mock batch processing
  - `test_retry_on_transient_error` - Mock Ollama fails then succeeds
  - `test_max_retries_exceeded` - Mock Ollama fails 3 times
  - `test_validate_connection_success` - Mock successful ping
  - `test_validate_model_missing` - Mock model not found
  - **Coverage Target**: 85%+ for EmbeddingService

- **Integration Tests** (`tests/integration/test_ollama_embedding.py`):
  - `test_real_ollama_embedding` - Call actual Ollama, verify 768 dims
  - `test_batch_embedding_performance` - 100 chunks in <10 seconds
  - **Requires**: Ollama running with nomic-embed-text model

**Code Quality Checklist:**
- [ ] Black formatting applied
- [ ] Ruff linting passed
- [ ] Type hints: `List[float]` for embeddings
- [ ] Google-style docstrings
- [ ] Logging: `logger.info("Generated {count} embeddings")`
- [ ] Error messages include troubleshooting steps

---

### Story 4.3: Create Vector Database Schema and Storage

**Story File:** [4.3-create-vector-database-schema-storage.md](../stories/4.3-create-vector-database-schema-storage.md) *(to be created by SM)*

**As a** developer,
**I want** to store embeddings in pgvector with metadata,
**so that** I can perform similarity searches.

**Acceptance Criteria:**
1. Alembic migration `create_embeddings_table.py` creates `embeddings` table with all fields
2. pgvector extension enabled: `CREATE EXTENSION IF NOT EXISTS vector;`
3. Indexes: `embeddings_project_id_idx`, `embeddings_project_doc_id_idx`, vector index (HNSW, m=16, ef_construction=64)
4. Metadata JSONB stores: `file_path`, `file_name`, `file_type`, `chunk_position`, `total_chunks`
5. `header_anchor` VARCHAR(512) nullable, default NULL
6. Repository method `create_embedding()` and `create_embeddings_batch()` (bulk insert)
7. Unit tests: 5+ tests in `tests/unit/repositories/test_embedding_repository.py`
8. Integration test: `tests/integration/test_embedding_storage.py` - store 100+ embeddings, query by project_id

**Implementation Notes:**
- **Migration File**: `backend/alembic/versions/{hash}_create_embeddings_table.py`
  ```python
  def upgrade():
      op.execute('CREATE EXTENSION IF NOT EXISTS vector')
      op.create_table(
          'embeddings',
          sa.Column('id', UUID(), primary_key=True, default=uuid.uuid4),
          sa.Column('project_id', UUID(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
          sa.Column('project_doc_id', UUID(), sa.ForeignKey('project_docs.id', ondelete='CASCADE'), nullable=False),
          sa.Column('document_id', UUID(), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
          sa.Column('chunk_text', sa.Text(), nullable=False),
          sa.Column('chunk_index', sa.Integer(), nullable=False),
          sa.Column('embedding', Vector(768), nullable=False),  # pgvector type
          sa.Column('header_anchor', sa.String(512), nullable=True),
          sa.Column('metadata', JSONB(), nullable=False),
          sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
      )
      # Indexes
      op.create_index('embeddings_project_id_idx', 'embeddings', ['project_id'])
      op.create_index('embeddings_project_doc_id_idx', 'embeddings', ['project_doc_id'])
      op.create_index('embeddings_document_id_idx', 'embeddings', ['document_id'])
      # Vector index: HNSW for fast approximate search
      op.execute('CREATE INDEX embeddings_vector_idx ON embeddings USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)')
  ```

- **Model Location**: `backend/app/models/embedding.py`
  ```python
  from pgvector.sqlalchemy import Vector

  class Embedding(Base):
      __tablename__ = "embeddings"
      id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
      project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
      project_doc_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("project_docs.id", ondelete="CASCADE"))
      document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
      chunk_text: Mapped[str] = mapped_column(Text)
      chunk_index: Mapped[int]
      embedding: Mapped[Vector] = mapped_column(Vector(768))
      header_anchor: Mapped[str | None] = mapped_column(String(512))
      metadata: Mapped[dict] = mapped_column(JSONB)
      created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  ```

- **Repository Location**: `backend/app/repositories/embedding_repository.py`
  ```python
  async def create_embeddings_batch(self, embeddings: List[EmbeddingCreate]) -> List[Embedding]:
      """Bulk insert embeddings for performance."""
      db_embeddings = [Embedding(**emb.model_dump()) for emb in embeddings]
      self.db.add_all(db_embeddings)
      await self.db.flush()
      return db_embeddings
  ```

- **Schema Location**: `backend/app/schemas/embedding.py`
  ```python
  class EmbeddingCreate(BaseModel):
      project_id: UUID
      project_doc_id: UUID
      document_id: UUID
      chunk_text: str
      chunk_index: int
      embedding: List[float]  # Will be converted to Vector
      header_anchor: Optional[str] = None
      metadata: dict
  ```

- **Index Choice**: HNSW (Hierarchical Navigable Small World) for <500ms search (per NFR4)
  - **IVFFlat**: Faster indexing, slower search (use for >1M vectors)
  - **HNSW**: Slower indexing, faster search (use for <1M vectors - our case)

**Testing Requirements:**
- **Unit Tests** (`tests/unit/repositories/test_embedding_repository.py`):
  - `test_create_embedding` - Insert single embedding
  - `test_create_embeddings_batch` - Bulk insert 10 embeddings
  - `test_foreign_key_cascade_delete` - Delete project, verify embeddings deleted
  - `test_metadata_jsonb_storage` - Verify JSONB fields stored correctly
  - `test_vector_dimension_validation` - Wrong dimension raises error
  - **Coverage Target**: 80%+

- **Integration Tests** (`tests/integration/test_embedding_storage.py`):
  - `test_store_100_embeddings` - Bulk insert, verify count
  - `test_query_by_project_id` - Filter embeddings by project
  - `test_vector_index_performance` - Similarity search <500ms
  - **Requires**: PostgreSQL with pgvector extension

**Code Quality Checklist:**
- [ ] Migration tested: `alembic upgrade head` then `alembic downgrade -1`
- [ ] Black formatting applied
- [ ] Ruff linting passed
- [ ] Type hints: `Vector` type properly imported from `pgvector.sqlalchemy`
- [ ] CASCADE delete verified for all FKs
- [ ] Migration includes rollback (`downgrade()` function)

---

### Story 4.4: Implement Header Anchor Extraction During Chunking

**Story File:** [4.4-implement-header-anchor-extraction.md](../stories/4.4-implement-header-anchor-extraction.md) *(to be created by SM)*

**As a** developer,
**I want** to identify and store header anchors for each chunk,
**so that** source links can navigate to specific document sections.

**Acceptance Criteria:**
1. `DoclingService` identifies nearest preceding header (H1-H3) for each markdown chunk
2. Method `_extract_header_anchor(text: str, chunk_start_pos: int) -> str | None`: converts header to anchor format
3. Anchor format: lowercase, spaces→hyphens, remove special chars (e.g., "## Architecture Overview" → "architecture-overview")
4. Anchor stored in `Chunk.metadata['header_anchor']` field (used by Story 4.3 when storing)
5. Fallback: If no header found before chunk, `header_anchor = None`
6. Unit tests: 6+ tests in `tests/unit/services/test_header_anchor_extraction.py`
7. Integration test: Process BMAD PRD.md (10+ sections), verify 90%+ chunks have anchors

**Implementation Notes:**
- **Anchor Extraction Logic** (in `DoclingService`):
  ```python
  import re

  def _extract_header_anchor(self, markdown_text: str, chunk_start_pos: int) -> str | None:
      """Find nearest preceding header and convert to anchor."""
      # Get text before chunk position
      text_before = markdown_text[:chunk_start_pos]

      # Find all headers (H1-H3) using regex
      header_pattern = r'^(#{1,3})\s+(.+)$'
      headers = list(re.finditer(header_pattern, text_before, re.MULTILINE))

      if not headers:
          return None  # No header found

      # Get last header before chunk
      last_header = headers[-1].group(2).strip()

      # Convert to anchor format
      anchor = last_header.lower()
      anchor = re.sub(r'[^\w\s-]', '', anchor)  # Remove special chars
      anchor = re.sub(r'[-\s]+', '-', anchor)   # Spaces to hyphens
      anchor = anchor.strip('-')                # Remove leading/trailing hyphens

      return anchor
  ```

- **Integration with Chunking** (Story 4.1 update):
  ```python
  def process_markdown(self, content: str) -> List[Chunk]:
      chunks = self.hybrid_chunker.chunk(content)
      result = []
      for idx, chunk in enumerate(chunks):
          anchor = self._extract_header_anchor(content, chunk.start_position)
          result.append(Chunk(
              text=chunk.text,
              index=idx,
              metadata={
                  'header_anchor': anchor,
                  # ... other metadata
              }
          ))
      return result
  ```

- **Anchor Format Examples**:
  - `## Epic Goal` → `epic-goal`
  - `### Story 4.1: Integration` → `story-41-integration`
  - `# BMADFlow PRD` → `bmadflow-prd`
  - No header → `None`

**Testing Requirements:**
- **Unit Tests** (`tests/unit/services/test_header_anchor_extraction.py`):
  - `test_extract_h1_header` - H1 header extraction
  - `test_extract_h2_header` - H2 header extraction
  - `test_extract_h3_header` - H3 header extraction
  - `test_no_header_returns_none` - Chunk at file start, no header
  - `test_special_chars_removed` - "Overview & Setup" → "overview-setup"
  - `test_multiple_headers_uses_nearest` - Gets last header before chunk
  - `test_ignore_h4_h5_h6` - Only H1-H3 considered
  - **Coverage Target**: 90%+

- **Integration Tests** (`tests/integration/test_header_anchor_extraction.py`):
  - `test_process_bmad_prd_anchors` - Process actual PRD.md, verify anchors
  - `test_anchor_coverage_90_percent` - At least 90% of chunks have anchors
  - `test_duplicate_headers_handled` - Multiple sections with same name

**Code Quality Checklist:**
- [ ] Black formatting applied
- [ ] Ruff linting passed
- [ ] Type hints: `str | None` for optional anchor
- [ ] Google-style docstrings
- [ ] Logging: `logger.debug(f"Extracted anchor: {anchor} for chunk {idx}")`
- [ ] Edge cases handled: empty headers, duplicate anchors

---

### Story 4.5: Build Sync-to-Embedding Pipeline

**Story File:** [4.5-build-sync-to-embedding-pipeline.md](../stories/4.5-build-sync-to-embedding-pipeline.md) *(to be created by SM)*

**As a** user,
**I want** documents automatically processed and indexed during sync,
**so that** they're immediately available for AI chatbot queries.

**Acceptance Criteria:**
1. `ProjectDocService.sync()` extended to call embedding pipeline after document storage
2. Pipeline: Download → Store Document → Chunk (Docling) → Generate Embeddings (Ollama) → Store Embeddings
3. Logging: `logger.info("Processing file {idx}/{total}: {file_path}")` for each file
4. Async processing: Use `asyncio.gather()` for parallel embedding generation (5 files at a time)
5. Error handling: Log error, continue sync, return summary with failed_files count
6. Performance: Complete sync+indexing in <5min per ProjectDoc (per NFR3)
7. Integration test: `tests/integration/test_sync_pipeline.py` - sync ProjectDoc with 10 files, verify all tables populated

**Implementation Notes:**
- **Service Updates** (`app/services/project_doc_service.py`):
  ```python
  async def sync(self, project_doc_id: UUID) -> SyncResult:
      # Existing sync logic (download files, store in documents table)
      documents = await self._download_and_store_documents(project_doc_id)

      # NEW: Embedding pipeline
      logger.info(f"Starting embedding pipeline for {len(documents)} documents")
      failed_files = []

      # Process in batches of 5 for parallel embedding generation
      for batch in self._batch(documents, size=5):
          tasks = [self._process_and_embed_document(doc) for doc in batch]
          results = await asyncio.gather(*tasks, return_exceptions=True)

          for doc, result in zip(batch, results):
              if isinstance(result, Exception):
                  logger.error(f"Failed to embed {doc.file_path}: {result}")
                  failed_files.append(doc.file_path)

      return SyncResult(
          success=True,
          documents_synced=len(documents),
          embeddings_created=len(documents) - len(failed_files),
          failed_files=failed_files
      )

  async def _process_and_embed_document(self, document: Document):
      """Process single document through embedding pipeline."""
      # 1. Chunk with Docling
      chunks = await self.docling_service.process_document(
          content=document.content,
          file_type=document.file_type
      )

      # 2. Generate embeddings with Ollama (batch)
      chunk_texts = [chunk.text for chunk in chunks]
      embeddings = await self.embedding_service.generate_embeddings_batch(chunk_texts)

      # 3. Store in embeddings table
      embedding_creates = []
      for chunk, embedding in zip(chunks, embeddings):
          embedding_creates.append(EmbeddingCreate(
              project_id=document.project_doc.project_id,
              project_doc_id=document.project_doc_id,
              document_id=document.id,
              chunk_text=chunk.text,
              chunk_index=chunk.index,
              embedding=embedding,
              header_anchor=chunk.metadata.get('header_anchor'),
              metadata={
                  'file_path': document.file_path,
                  'file_name': document.file_path.split('/')[-1],
                  'file_type': document.file_type,
                  'chunk_position': chunk.index,
                  'total_chunks': len(chunks)
              }
          ))

      await self.embedding_repository.create_embeddings_batch(embedding_creates)
      logger.info(f"Embedded {len(embeddings)} chunks from {document.file_path}")
  ```

- **Schema Updates** (`app/schemas/project_doc.py`):
  ```python
  class SyncResult(BaseModel):
      success: bool
      documents_synced: int
      embeddings_created: int
      failed_files: List[str] = []
      duration_seconds: float
  ```

- **Error Recovery Strategy**:
  - Embedding failure for one file doesn't stop entire sync
  - Failed files logged with stack trace
  - User sees summary: "10/12 files successfully indexed (2 failed)"
  - Failed files can be retried individually via re-sync

- **Performance Optimization**:
  - Parallel processing: 5 documents at a time (configurable)
  - Batch embedding generation: 10 chunks per Ollama call
  - Target: 10 files with 100 chunks each = ~5 min total

**Testing Requirements:**
- **Integration Tests** (`tests/integration/test_sync_pipeline.py`):
  - `test_sync_pipeline_end_to_end` - Sync ProjectDoc, verify documents + embeddings tables
  - `test_sync_with_partial_failure` - Mock Ollama fails on 1 file, others succeed
  - `test_sync_performance_5min_limit` - 20 files complete in <5 min
  - `test_embedding_metadata_complete` - Verify all metadata fields populated
  - `test_header_anchors_extracted` - Verify 90%+ chunks have anchors
  - **Requires**: Ollama running, test GitHub repo with sample files

- **Unit Tests** (`tests/unit/services/test_project_doc_service.py`):
  - `test_batch_processing` - Verify documents batched correctly
  - `test_error_handling_continues_sync` - Exception in one batch doesn't stop others
  - **Coverage Target**: 75%+

**Code Quality Checklist:**
- [ ] Black formatting applied
- [ ] Ruff linting passed
- [ ] Type hints: `async def` for all pipeline functions
- [ ] Google-style docstrings
- [ ] Logging: Progress updates every file, summary at end
- [ ] Performance measured: Log total duration in seconds

---

### Story 4.6: Implement Vector Similarity Search API

**Story File:** [4.6-implement-vector-similarity-search-api.md](../stories/4.6-implement-vector-similarity-search-api.md) *(to be created by SM)*

**As a** developer,
**I want** to perform vector similarity searches filtered by Project,
**so that** I can retrieve relevant chunks for RAG queries.

**Acceptance Criteria:**
1. REST API endpoint `POST /api/projects/{project_id}/search` accepts `SearchRequest` and returns `SearchResponse`
2. Generate query embedding using `EmbeddingService.generate_embedding(query_text)`
3. pgvector cosine similarity search: `ORDER BY embedding <=> query_embedding LIMIT k`
4. Filter: `WHERE project_id = {project_id}` (scoped to Project)
5. Return top-k results (k=5 default, max 20): `chunk_text`, `metadata`, `similarity_score`, `document_id`, `header_anchor`
6. Performance: Search completes in <500ms (per NFR4) - verified with EXPLAIN ANALYZE
7. Unit tests: 4+ tests in `tests/unit/api/test_search_api.py`
8. Integration test: Index 100+ docs, search, verify top-5 relevance

**Implementation Notes:**
- **API Endpoint** (`app/api/v1/search.py`):
  ```python
  @router.post("/projects/{project_id}/search", response_model=SearchResponse)
  async def search_embeddings(
      project_id: UUID,
      request: SearchRequest,
      embedding_service: EmbeddingService = Depends(get_embedding_service),
      embedding_repo: EmbeddingRepository = Depends(get_embedding_repository)
  ):
      # 1. Generate query embedding
      query_embedding = await embedding_service.generate_embedding(request.query)

      # 2. Vector similarity search
      results = await embedding_repo.similarity_search(
          project_id=project_id,
          query_embedding=query_embedding,
          limit=request.top_k or 5
      )

      # 3. Format response
      return SearchResponse(
          query=request.query,
          results=[
              SearchResult(
                  chunk_text=r.chunk_text,
                  similarity_score=r.similarity_score,
                  document_id=r.document_id,
                  header_anchor=r.header_anchor,
                  metadata=r.metadata
              ) for r in results
          ],
          total_results=len(results)
      )
  ```

- **Repository Method** (`app/repositories/embedding_repository.py`):
  ```python
  async def similarity_search(
      self,
      project_id: UUID,
      query_embedding: List[float],
      limit: int = 5
  ) -> List[EmbeddingSearchResult]:
      """Perform cosine similarity search using pgvector."""
      query = select(
          Embedding,
          Embedding.embedding.cosine_distance(query_embedding).label('distance')
      ).where(
          Embedding.project_id == project_id
      ).order_by(
          'distance'  # Ascending order (lower distance = higher similarity)
      ).limit(limit)

      result = await self.db.execute(query)
      rows = result.all()

      return [
          EmbeddingSearchResult(
              chunk_text=row.Embedding.chunk_text,
              similarity_score=1 - row.distance,  # Convert distance to similarity
              document_id=row.Embedding.document_id,
              header_anchor=row.Embedding.header_anchor,
              metadata=row.Embedding.metadata
          ) for row in rows
      ]
  ```

- **Schemas** (`app/schemas/search.py`):
  ```python
  class SearchRequest(BaseModel):
      query: str
      top_k: int = 5  # Max 20

      @validator('top_k')
      def validate_top_k(cls, v):
          if v < 1 or v > 20:
              raise ValueError('top_k must be between 1 and 20')
          return v

  class SearchResult(BaseModel):
      chunk_text: str
      similarity_score: float  # 0.0 to 1.0
      document_id: UUID
      header_anchor: str | None
      metadata: dict

  class SearchResponse(BaseModel):
      query: str
      results: List[SearchResult]
      total_results: int
  ```

- **Performance Notes**:
  - Cosine distance: `embedding <=> query_embedding` (pgvector operator)
  - HNSW index (from Story 4.3) enables <500ms search
  - EXPLAIN ANALYZE to verify index usage: `Index Scan using embeddings_vector_idx`

**Testing Requirements:**
- **Unit Tests** (`tests/unit/api/test_search_api.py`):
  - `test_search_endpoint_success` - Mock valid search, verify response format
  - `test_search_top_k_validation` - Invalid top_k raises 422
  - `test_search_filters_by_project` - Verify project_id filtering
  - `test_search_empty_results` - No matches returns empty list
  - **Coverage Target**: 85%+

- **Integration Tests** (`tests/integration/test_vector_search.py`):
  - `test_search_relevance_ranking` - Index sample docs, verify top result matches query
  - `test_search_performance_500ms` - 100+ chunks searched in <500ms
  - `test_search_with_header_anchors` - Results include valid anchors
  - `test_cross_project_isolation` - Project A search doesn't return Project B chunks
  - **Requires**: PostgreSQL with embeddings indexed

- **Performance Test** (`tests/performance/test_search_performance.py`):
  - `test_search_latency_p95` - 95th percentile <500ms over 100 queries
  - Use `EXPLAIN ANALYZE` to verify index usage

**Code Quality Checklist:**
- [ ] Black formatting applied
- [ ] Ruff linting passed
- [ ] Type hints: `List[float]` for query_embedding
- [ ] Google-style docstrings
- [ ] OpenAPI docs: Add request/response examples
- [ ] Logging: `logger.info(f"Search: '{query}' returned {count} results in {duration}ms")`
- [ ] Performance: Verify HNSW index used (check query plan)

---

## Testing Architecture & QA Requirements

### Test Coverage Targets (per NFR18)
- **Backend Overall**: 70%+ coverage
- **Service Layer**: 80%+ coverage
- **Repository Layer**: 80%+ coverage
- **API Layer**: 85%+ coverage

### Test File Structure
```
backend/tests/
├── unit/
│   ├── services/
│   │   ├── test_docling_service.py (Story 4.1 - 6 tests)
│   │   ├── test_embedding_service.py (Story 4.2 - 7 tests)
│   │   ├── test_header_anchor_extraction.py (Story 4.4 - 7 tests)
│   │   └── test_project_doc_service.py (Story 4.5 - 2 tests)
│   ├── repositories/
│   │   └── test_embedding_repository.py (Story 4.3 - 5 tests)
│   └── api/
│       └── test_search_api.py (Story 4.6 - 4 tests)
├── integration/
│   ├── test_document_processing.py (Story 4.1 - 3 tests)
│   ├── test_ollama_embedding.py (Story 4.2 - 2 tests)
│   ├── test_embedding_storage.py (Story 4.3 - 3 tests)
│   ├── test_header_anchor_extraction.py (Story 4.4 - 3 tests)
│   ├── test_sync_pipeline.py (Story 4.5 - 5 tests)
│   └── test_vector_search.py (Story 4.6 - 4 tests)
└── performance/
    └── test_search_performance.py (Story 4.6 - 1 test)
```

### QA Gate Requirements

Each story requires QA gate file at `docs/qa/gates/4.X-{story-name}.yml` with:
- Schema version: 1
- Gate status: PASS/FAIL
- NFR validation (security, performance, reliability, maintainability)
- Quality score: 0-100
- Risk summary (critical/high/medium/low issue counts)
- Test evidence (tests reviewed, ACs covered, gaps identified)

**Template** (from Epic 3 pattern):
```yaml
schema: 1
story: "4.X"
story_title: "{Story Title}"
gate: PASS  # or FAIL
status_reason: "{Brief explanation}"
reviewer: "Quinn (Test Architect)"
updated: "2025-XX-XXT00:00:00Z"

waiver: { active: false }
top_issues: []

evidence:
  tests_reviewed: X
  risks_identified: 0
  trace:
    ac_covered: [1, 2, 3, ...]
    ac_gaps: []

nfr_validation:
  security: { status: PASS, notes: "..." }
  performance: { status: PASS, notes: "..." }
  reliability: { status: PASS, notes: "..." }
  maintainability: { status: PASS, notes: "..." }

quality_score: 95
risk_summary:
  totals: { critical: 0, high: 0, medium: 0, low: 0 }
```

### E2E Test Scenarios (Optional - Nice to Have)

**Scenario 1: Complete RAG Pipeline**
1. Create Project
2. Create ProjectDoc with test GitHub repo
3. Sync ProjectDoc (triggers embedding pipeline)
4. Verify embeddings table populated
5. Perform vector search
6. Verify relevant results returned with header anchors

**Scenario 2: Performance Validation**
1. Index 100+ documents (1000+ chunks)
2. Run 100 search queries
3. Measure P95 latency < 500ms
4. Verify HNSW index used (EXPLAIN ANALYZE)

---

## Definition of Done

### Must Complete (All P0)
- [x] **Story 4.1**: Docling integrated, chunking all file types (MD, CSV, YAML, JSON) ✅
  - [x] 10 unit tests passing (exceeds 6+ requirement)
  - [x] 5 integration tests passing (exceeds 3+ requirement)
  - [x] QA gate: PASS (score 95/100)
  - [x] Code quality: Black/Ruff clean
  - **Status**: Done | **Completed**: 2025-10-09

- [ ] **Story 4.2**: Ollama embeddings working with nomic-embed-text
  - [ ] Startup validation implemented (connection + model check)
  - [ ] Retry logic with exponential backoff (3 attempts, 30s max)
  - [ ] 7+ unit tests passing (mocked Ollama)
  - [ ] 2+ integration tests passing (real Ollama)
  - [ ] QA gate: PASS (score 90+)

- [ ] **Story 4.3**: pgvector schema created with HNSW index
  - [ ] Alembic migration tested (upgrade + downgrade)
  - [ ] Embedding model + repository + schema created
  - [ ] Bulk insert working (100+ embeddings)
  - [ ] 5+ unit tests passing
  - [ ] 3+ integration tests passing
  - [ ] QA gate: PASS (score 90+)

- [ ] **Story 4.4**: Header anchor extraction implemented
  - [ ] Anchor extraction for H1-H3 headers
  - [ ] Fallback to null if no header found
  - [ ] 90%+ chunks have anchors (integration test verified)
  - [ ] 7+ unit tests passing
  - [ ] 3+ integration tests passing
  - [ ] QA gate: PASS (score 90+)

- [ ] **Story 4.5**: Sync pipeline extended with embedding generation
  - [ ] Async processing (5 files parallel, 10 chunks/batch)
  - [ ] Error handling: partial failures don't stop sync
  - [ ] Performance: <5min per ProjectDoc (NFR3)
  - [ ] 2+ unit tests passing
  - [ ] 5+ integration tests passing
  - [ ] QA gate: PASS (score 90+)

- [ ] **Story 4.6**: Vector similarity search API working
  - [ ] POST /api/projects/{id}/search endpoint
  - [ ] Cosine similarity with HNSW index
  - [ ] Performance: <500ms search (NFR4)
  - [ ] 4+ unit tests passing
  - [ ] 4+ integration tests passing
  - [ ] Performance test: P95 <500ms
  - [ ] QA gate: PASS (score 90+)

### Epic-Level Requirements
- [ ] **Overall Test Coverage**: 70%+ backend coverage (pytest-cov)
- [ ] **All QA Gates**: 6/6 stories with PASS status
- [ ] **Performance Validation**:
  - [ ] Sync pipeline: <5min per ProjectDoc (NFR3)
  - [ ] Vector search: <500ms per query (NFR4)
  - [ ] EXPLAIN ANALYZE confirms HNSW index usage
- [ ] **Code Quality**:
  - [ ] All code formatted with Black
  - [ ] All code linted with Ruff (zero errors)
  - [ ] Type hints on all functions
  - [ ] Google-style docstrings
- [ ] **Documentation**:
  - [ ] All API endpoints in OpenAPI/Swagger
  - [ ] Migration files include docstrings
  - [ ] README updated with Ollama setup instructions
- [ ] **Integration Validation**:
  - [ ] End-to-end test: Sync → Index → Search (working)
  - [ ] Cross-story integration verified
  - [ ] All dependencies properly injected

### Handoff to Epic 5 (AI Chatbot)
- [ ] Vector search API documented for chatbot consumption
- [ ] Sample queries + responses documented
- [ ] Performance characteristics documented (latency, throughput)
- [ ] Error handling patterns documented
