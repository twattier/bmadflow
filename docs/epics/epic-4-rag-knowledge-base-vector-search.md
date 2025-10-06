# Epic 4: RAG Knowledge Base & Vector Search

## Epic Goal

Implement the RAG infrastructure using Docling for document processing, Ollama for embeddings, pgvector for storage, and build vector similarity search to power the AI chatbot.

## Stories

### Story 4.1: Integrate Docling Library and Document Processing Pipeline

**As a** developer,
**I want** to process synced documents using Docling's HybridChunker,
**so that** I can generate optimized chunks for RAG.

**Acceptance Criteria:**
1. Docling library integrated into backend (added to requirements.txt)
2. Document processing service created using Docling's HybridChunker with default settings
3. Function to process markdown files: serialize, chunk, extract metadata
4. Function to process CSV files: serialize, chunk by rows
5. Function to process YAML/JSON files: serialize, chunk by structure
6. Chunk size configured for technical documentation (Docling defaults acceptable)
7. Unit tests for document processing with sample BMAD docs
8. Integration test: process 10+ files, verify chunks generated

---

### Story 4.2: Implement Ollama Embedding Generation

**As a** developer,
**I want** to generate embeddings using Ollama with nomic-embed-text model,
**so that** I can create vector representations of document chunks.

**Acceptance Criteria:**
1. Ollama client library integrated (ollama-python)
2. Environment variable `OLLAMA_ENDPOINT_URL` configured (default: http://localhost:11434)
3. Backend validates Ollama connectivity on startup with clear error if unavailable
4. Backend validates nomic-embed-text model availability with instructions if missing
5. Function to generate embeddings: input text → output 768-dim vector
6. Batch processing: generate embeddings for multiple chunks efficiently
7. Error handling: retry on transient Ollama errors, fail gracefully with clear message
8. Unit tests with mocked Ollama responses
9. Integration test: generate embeddings for sample text, verify 768 dimensions

---

### Story 4.3: Create Vector Database Schema and Storage

**As a** developer,
**I want** to store embeddings in pgvector with metadata,
**so that** I can perform similarity searches.

**Acceptance Criteria:**
1. Alembic migration creates `embeddings` table: id (UUID), project_id (FK), project_doc_id (FK), document_id (FK), chunk_text (text), chunk_index (int), embedding (vector(768)), header_anchor (string, nullable), metadata (JSONB), created_at
2. pgvector extension used for embedding column
3. Indexes created: project_id, project_doc_id, vector index for similarity search (IVFFlat or HNSW)
4. Metadata JSONB stores: file_path, file_name, file_type, chunk_position, total_chunks
5. Header anchor field stores identified section heading (nullable, fallback to null if not identifiable)
6. Function to insert embeddings with metadata
7. Unit tests for embedding storage
8. Integration test: store 100+ embeddings, verify queryable

---

### Story 4.4: Implement Header Anchor Extraction During Chunking

**As a** developer,
**I want** to identify and store header anchors for each chunk,
**so that** source links can navigate to specific document sections.

**Acceptance Criteria:**
1. Document processing pipeline identifies nearest preceding header (H1-H3) for each chunk
2. Header text converted to anchor format (lowercase, hyphens, remove special chars)
3. Anchor stored in embeddings table header_anchor field
4. If no header found or header ambiguous, anchor set to null (graceful fallback)
5. Unit tests with markdown samples containing headers
6. Integration test: process BMAD PRD with multiple sections, verify anchors extracted

---

### Story 4.5: Build Sync-to-Embedding Pipeline

**As a** user,
**I want** documents automatically processed and indexed during sync,
**so that** they're immediately available for AI chatbot queries.

**Acceptance Criteria:**
1. Sync process extended to include embedding generation after file download
2. Pipeline: Download file → Store in documents table → Process with Docling → Generate embeddings with Ollama → Store in embeddings table
3. Sync process updates: "Processing file X of Y" logged
4. Background processing acceptable (async) - user notified when sync+indexing complete
5. Error handling: sync continues if embedding fails for one file, logs error
6. Performance: sync+indexing completes in <5 minutes per ProjectDoc (per NFR3)
7. Integration test: sync ProjectDoc, verify documents and embeddings tables populated

---

### Story 4.6: Implement Vector Similarity Search API

**As a** developer,
**I want** to perform vector similarity searches filtered by Project,
**so that** I can retrieve relevant chunks for RAG queries.

**Acceptance Criteria:**
1. REST API endpoint `POST /api/projects/{id}/search` accepts query text and returns top-k chunks
2. Query processing: generate embedding for query text using Ollama
3. Vector similarity search using pgvector (cosine similarity or L2 distance)
4. Filter results by project_id to scope to specific Project
5. Return top-k results (k=5 default, configurable) with: chunk_text, metadata, similarity_score, document_id, header_anchor
6. Performance: search completes in <500ms (per NFR4)
7. Unit tests with sample query
8. Integration test: index sample docs, perform search, verify relevant results returned

---

## Definition of Done

- [ ] All 6 stories completed with acceptance criteria met
- [ ] Docling integrated and processing documents into chunks
- [ ] Ollama generating 768-dim embeddings with nomic-embed-text
- [ ] pgvector storing embeddings with metadata and header anchors
- [ ] Sync pipeline automatically indexes documents
- [ ] Vector similarity search returns relevant results in <500ms
- [ ] All API endpoints documented in OpenAPI/Swagger
- [ ] Unit and integration tests passing
- [ ] Performance targets met (NFR3, NFR4)
