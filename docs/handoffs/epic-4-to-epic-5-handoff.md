# Epic 4 → Epic 5 Handoff Document

**From**: Epic 4 - RAG Knowledge Base & Vector Search
**To**: Epic 5 - AI Chatbot Integration
**Handoff Date**: 2025-10-13
**Status**: ✅ Production-Ready Infrastructure

---

## Executive Summary

Epic 4 has successfully delivered a **production-ready RAG infrastructure** with zero blocking issues. The vector search API is ready for consumption by the AI chatbot, with comprehensive documentation, tested performance, and established error handling patterns.

**Ready for Epic 5**: ✅ YES - All prerequisites met, zero blockers

---

## What Epic 4 Delivered

### Core Infrastructure ✅

1. **Document Processing Pipeline** (Story 4.1)
   - Docling HybridChunker integration
   - Support for MD, CSV, YAML, JSON files
   - Semantic chunking with metadata preservation

2. **Embedding Generation** (Story 4.2)
   - Ollama integration with nomic-embed-text (768-dim)
   - Startup validation (connection + model check)
   - Retry logic with exponential backoff

3. **Vector Storage** (Story 4.3)
   - PostgreSQL + pgvector (`chunks` table)
   - HNSW index (m=16, ef_construction=64)
   - Bulk insert optimization (100+ chunks)

4. **Header Anchor Extraction** (Story 4.4)
   - GitHub-style anchor format (H1-H3 headers)
   - 90%+ coverage for navigation
   - Fallback to null for chunks without headers

5. **Sync-to-Embedding Pipeline** (Story 4.5)
   - End-to-end: Download → Chunk → Embed → Store
   - Async processing (5 files parallel)
   - Graceful error handling (partial failures)

6. **Vector Search API** (Story 4.6)
   - REST endpoint: `POST /api/projects/{project_id}/search`
   - Cosine similarity with HNSW index
   - Performance: <500ms per query (validated)

---

## Vector Search API - Ready for Consumption

### Endpoint

```
POST /api/projects/{project_id}/search
```

### Request Schema

```json
{
  "query": "string",      // User's question (required)
  "top_k": 5              // Number of results (1-20, default: 5)
}
```

### Response Schema (200 OK)

```json
{
  "query": "string",
  "results": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "chunk_text": "string",          // The relevant text chunk
      "similarity_score": 0.0-1.0,     // Cosine similarity (1.0 = perfect match)
      "header_anchor": "string | null", // GitHub-style anchor for navigation
      "metadata": {
        "file_path": "string",         // Full path in repo
        "file_name": "string",         // Just the filename
        "file_type": "md | csv | yaml | json",
        "chunk_position": "integer",   // Index in document
        "total_chunks": "integer"      // Total chunks in document
      }
    }
  ],
  "total_results": "integer"
}
```

### Error Responses

| Code | Reason | Response |
|------|--------|----------|
| `404` | Project not found | `{"detail": "Project not found"}` |
| `422` | Invalid request | `{"detail": "Validation error: ..."}` |
| `500` | Service error | `{"detail": "Internal server error"}` |

**Common 422 Validation Errors**:
- Empty query string
- `top_k` out of range (must be 1-20)

**Common 500 Service Errors**:
- Ollama service unavailable
- Database connection error
- Embedding generation failure

### Example Usage

**Request**:
```bash
curl -X POST "http://localhost:8000/api/projects/{project_id}/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does the RAG pipeline work?",
    "top_k": 3
  }'
```

**Response**:
```json
{
  "query": "How does the RAG pipeline work?",
  "results": [
    {
      "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
      "document_id": "650e8400-e29b-41d4-a716-446655440001",
      "chunk_text": "The RAG pipeline consists of three main stages: document processing with Docling, embedding generation with Ollama, and vector storage in pgvector...",
      "similarity_score": 0.92,
      "header_anchor": "rag-pipeline-architecture",
      "metadata": {
        "file_path": "docs/architecture/rag-architecture.md",
        "file_name": "rag-architecture.md",
        "file_type": "md",
        "chunk_position": 3,
        "total_chunks": 12
      }
    },
    {
      "chunk_id": "550e8400-e29b-41d4-a716-446655440002",
      "document_id": "650e8400-e29b-41d4-a716-446655440001",
      "chunk_text": "RAG (Retrieval-Augmented Generation) enhances LLM responses by retrieving relevant context from a knowledge base before generating answers...",
      "similarity_score": 0.88,
      "header_anchor": "what-is-rag",
      "metadata": {
        "file_path": "docs/architecture/rag-architecture.md",
        "file_name": "rag-architecture.md",
        "file_type": "md",
        "chunk_position": 1,
        "total_chunks": 12
      }
    }
  ],
  "total_results": 2
}
```

### OpenAPI Documentation

Full API documentation available at: `http://localhost:8000/api/docs`

Includes:
- Interactive Swagger UI
- Request/response schemas
- Example requests
- Error response formats

---

## Performance Characteristics

### Validated Performance (NFRs Met)

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| **Vector Search** | <500ms | <500ms | ✅ Validated with 100+ chunks |
| **Sync Pipeline** | <5min | 2-3min | ✅ 10 files, 100 chunks |
| **Embedding Generation** | <10s | <5s | ✅ 10 chunks batch |

### HNSW Index Configuration

- **Index Type**: HNSW (Hierarchical Navigable Small World)
- **Parameters**: `m=16, ef_construction=64`
- **Optimized For**: <1M vectors (our use case)
- **Distance Metric**: Cosine distance (`<=>` operator)

**Performance Characteristics**:
- Sub-500ms search with 100+ chunks (validated)
- Linear scaling up to ~100K chunks
- Index build time: ~1s per 1000 chunks

### Embedding Model

- **Model**: nomic-embed-text (Ollama)
- **Dimensions**: 768
- **Generation Speed**: ~100ms per chunk (Ollama local)
- **Batch Size**: 10 chunks (optimal)

---

## Data Flow for Chatbot Integration

### Recommended RAG Flow

```
1. User asks question in chatbot UI
   ↓
2. Frontend sends question to chatbot backend
   ↓
3. Chatbot calls vector search API:
   POST /api/projects/{project_id}/search
   { "query": "user question", "top_k": 5 }
   ↓
4. Vector search returns relevant chunks with similarity scores
   ↓
5. Chatbot assembles context from top results:
   - Extract chunk_text from results
   - Include file_path and header_anchor for citations
   - Order by similarity_score (descending)
   ↓
6. Chatbot calls LLM with:
   - System prompt: "Answer based on context"
   - Context: Concatenated chunk_text
   - User question
   ↓
7. LLM generates response
   ↓
8. Chatbot returns response with source citations:
   - Use header_anchor for deep links
   - Use file_path for source references
   - Use similarity_score to indicate confidence
```

### Context Assembly Example

```python
# Pseudo-code for chatbot backend
async def generate_chatbot_response(project_id: UUID, user_question: str):
    # Step 1: Get relevant chunks
    search_response = await vector_search_api.search(
        project_id=project_id,
        query=user_question,
        top_k=5
    )

    # Step 2: Assemble context
    context_chunks = []
    sources = []

    for result in search_response.results:
        context_chunks.append(result.chunk_text)
        sources.append({
            "file": result.metadata.file_path,
            "anchor": result.header_anchor,
            "score": result.similarity_score
        })

    context = "\n\n---\n\n".join(context_chunks)

    # Step 3: Call LLM
    llm_response = await llm_client.generate(
        system_prompt="Answer the user's question based on the provided context. Cite sources when possible.",
        context=context,
        user_question=user_question
    )

    # Step 4: Return response with citations
    return {
        "answer": llm_response,
        "sources": sources
    }
```

### Source Citation Format

Use `header_anchor` for deep links in the Documentation Explorer:

```
Source: docs/architecture.md#rag-pipeline-architecture (Similarity: 92%)
```

Frontend can navigate to:
```
/projects/{project_id}/docs/{document_id}#rag-pipeline-architecture
```

---

## Critical Learnings for Epic 5

### 1. Session-Per-Task Pattern for Async Operations

**Context**: Story 4.5 discovered critical session management bug

**Problem**: Sharing database session across async tasks causes `DetachedInstanceError`

**Solution**: Each async task needs its own session

```python
# ❌ WRONG - Shared session across tasks
async def process_multiple_items(db: AsyncSession, items: List[Item]):
    tasks = [process_item(db, item) for item in items]
    await asyncio.gather(*tasks)

# ✅ CORRECT - Session per task
async def process_multiple_items(items: List[Item]):
    async def process_with_session(item: Item):
        async with AsyncSessionLocal() as db:
            await process_item(db, item)

    tasks = [process_with_session(item) for item in items]
    await asyncio.gather(*tasks)
```

**Recommendation**: If Epic 5 needs parallel chatbot requests, use session-per-task pattern.

### 2. Production Validation Non-Negotiable

**Context**: Stories 4.5 and 4.6 found issues during production testing

**Learning**: Unit tests with mocks don't expose all edge cases

**Recommendation**:
- Test with real Ollama service (not mocked)
- Test with production-like data volumes
- Test concurrent operations explicitly

### 3. Error Handling Best Practices

**Context**: All stories implement graceful degradation

**Patterns Established**:
- Retry with exponential backoff (Ollama errors)
- Partial failure handling (sync pipeline)
- Clear error messages with troubleshooting steps

**Recommendation**: Chatbot should handle vector search failures gracefully:
- Cache last successful search results
- Fallback to generic LLM response if search fails
- Clear error messages to user

### 4. Header Anchors for Navigation

**Context**: Story 4.4 achieved 90%+ anchor coverage

**Usage**: Search results include `header_anchor` for deep linking

**Recommendation**:
- Use anchors for "View Source" links in chatbot UI
- Navigate to specific section, not just file
- Show anchor in citation: `docs/architecture.md#section-name`

---

## Testing Recommendations for Epic 5

### Integration Tests

**Test Vector Search API from Chatbot**:
```python
async def test_chatbot_vector_search_integration():
    # Given: Project with indexed documents
    project_id = await create_test_project_with_docs()

    # When: Chatbot queries vector search
    response = await vector_search_api.search(
        project_id=project_id,
        query="How does authentication work?",
        top_k=5
    )

    # Then: Results are relevant and include metadata
    assert len(response.results) > 0
    assert response.results[0].similarity_score > 0.7
    assert response.results[0].header_anchor is not None
    assert "file_path" in response.results[0].metadata
```

### E2E Tests

**Test Complete RAG Flow**:
1. User asks question in chatbot
2. Chatbot queries vector search
3. Chatbot assembles context
4. Chatbot calls LLM
5. User sees response with citations
6. User clicks "View Source" → navigates to document with anchor

### Performance Tests

**Monitor Chatbot Response Time**:
- Vector search: <500ms (validated)
- LLM generation: <2s (to be validated in Epic 5)
- Total response time target: <3s (per NFR5)

---

## Known Issues & Limitations

### Minor Issues (Non-Blocking)

1. **Table Naming Inconsistency**
   - Epic docs originally referenced `embeddings` table
   - Implementation uses `chunks` table (semantically correct)
   - **Impact**: None - documentation updated
   - **Action**: None required

2. **Repository Pattern Variation**
   - Some repos use `__init__` injection, others use per-method
   - **Impact**: Low - both patterns work
   - **Action**: Future standardization (Epic 7+)

3. **FastAPI Lifespan Pattern**
   - Using deprecated `@app.on_event("startup")`
   - **Impact**: Low - still works in FastAPI 0.109+
   - **Action**: Migrate to lifespan (Epic 7+)

### Limitations (By Design)

1. **Project-Level Isolation Only**
   - Vector search scoped to Project (not User)
   - **Impact**: Acceptable for 3-user POC
   - **Future**: User-level isolation (Epic 8+)

2. **No Incremental Embedding**
   - Full re-sync regenerates all embeddings
   - **Impact**: Acceptable for POC (<100 files)
   - **Future**: Incremental embedding (Epic 7+)

3. **Single Embedding Model**
   - No migration strategy for model changes
   - **Impact**: Low - model stable for POC
   - **Future**: Versioned embeddings (Epic 8+)

---

## Dependencies & Setup

### Required Services

**Ollama** (Already configured in Epic 4):
```bash
# Verify Ollama running
curl http://localhost:11434/api/version

# Verify model installed
ollama list | grep nomic-embed-text
```

**PostgreSQL with pgvector** (Already configured):
```bash
# Verify extension
psql -h localhost -U postgres -d bmadflow -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Environment Variables

**Already configured in `.env`**:
```bash
OLLAMA_ENDPOINT_URL=http://localhost:11434
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/bmadflow
```

**Epic 5 may need**:
```bash
LLM_PROVIDER=ollama  # or openai, anthropic
LLM_MODEL=llama3     # or gpt-4, claude-3-opus
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=500
```

---

## Code References

### Key Files for Epic 5 Integration

**Vector Search API**:
- Endpoint: [`app/api/v1/search.py`](../../backend/app/api/v1/search.py)
- Schema: [`app/schemas/search.py`](../../backend/app/schemas/search.py)

**Services**:
- Embedding: [`app/services/embedding_service.py`](../../backend/app/services/embedding_service.py)
- Chunk Repository: [`app/repositories/chunk_repository.py`](../../backend/app/repositories/chunk_repository.py)

**Models**:
- Chunk: [`app/models/chunk.py`](../../backend/app/models/chunk.py)

**Documentation**:
- Story 4.6: [`docs/stories/4.6-implement-vector-similarity-search-api.md`](../stories/4.6-implement-vector-similarity-search-api.md)
- Epic 4: [`docs/epics/epic-4-rag-knowledge-base-vector-search.md`](../epics/epic-4-rag-knowledge-base-vector-search.md)

---

## Action Items for Epic 5 Team

### Before Starting Story 5.1

- [ ] Review vector search API documentation (this document)
- [ ] Test vector search endpoint with sample queries
- [ ] Verify Ollama and pgvector setup
- [ ] Review session-per-task pattern (if using async parallelism)
- [ ] Plan LLM integration (provider, model, prompts)

### During Epic 5 Development

- [ ] Add concurrent stress tests to chatbot testing checklist
- [ ] Document LLM prompting strategy
- [ ] Test with production-like data (100+ chunks)
- [ ] Implement source citation UI with header anchors
- [ ] Monitor chatbot response time (<3s target)

### Nice to Have

- [ ] Implement caching for frequent queries
- [ ] Add feedback mechanism (thumbs up/down on responses)
- [ ] Track similarity score thresholds for quality

---

## Questions & Support

### Common Questions

**Q: How do I test the vector search API?**
A: Use the interactive Swagger UI at `http://localhost:8000/api/docs` or curl:
```bash
curl -X POST "http://localhost:8000/api/projects/{project_id}/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "top_k": 5}'
```

**Q: What if Ollama is unavailable?**
A: The API will return a 500 error with clear message. Implement fallback logic in chatbot (e.g., generic LLM response without context).

**Q: How do I navigate to a specific section in the Documentation Explorer?**
A: Use the `header_anchor` from search results:
```
/projects/{project_id}/docs/{document_id}#{header_anchor}
```

**Q: What similarity score is "good enough"?**
A: Based on testing:
- `> 0.8`: Highly relevant
- `0.6 - 0.8`: Relevant
- `< 0.6`: Potentially not relevant (consider excluding)

**Q: Can I change the embedding model?**
A: Not recommended for POC. Changing models requires re-embedding all documents (no migration strategy yet).

### Contact Points

- **Epic 4 Lead**: James (Dev Agent) - via retrospective docs
- **QA Lead**: Quinn - QA gate files in `docs/qa/gates/`
- **Product Owner**: Sarah - PRD and epic approval

---

## Success Criteria for Epic 5

### Must Have (P0)

- [ ] Chatbot UI component integrated
- [ ] Vector search API consumed successfully
- [ ] Context assembly from search results working
- [ ] LLM integration functional
- [ ] Source citations with header anchor navigation
- [ ] Response time <3s (per NFR5)

### Should Have (P1)

- [ ] Error handling for vector search failures
- [ ] Caching for frequent queries
- [ ] Similarity score threshold tuning

### Nice to Have (P2)

- [ ] User feedback mechanism (thumbs up/down)
- [ ] Conversation history
- [ ] Multi-turn context retention

---

## Appendix: Epic 4 Retrospective Summary

**Full Retrospective**: [Epic 4 Retrospective](../retrospectives/epic-4-retrospective.md)

### Key Takeaways

1. **Session-per-task pattern critical** for async database operations
2. **Production validation non-negotiable** for quality
3. **Per-story QA gates prevent defect accumulation** (avg 95.8/100 quality)
4. **Consistent patterns accelerate development** (stories 4.4-4.6 faster)
5. **Comprehensive testing pays dividends** (120 tests, 0 blocking issues)

### Metrics Achieved

- 6/6 stories complete (100%)
- 120 tests, 100% pass rate
- Average quality score: 95.8/100
- Zero blocking issues
- Performance: Search <500ms ✓, Sync <5min ✓

---

**Document Status**: Final
**Author**: Epic 4 Team (James, Sarah, Quinn)
**Handoff Date**: 2025-10-13
**Next Epic**: Epic 5 - AI Chatbot Integration

**Ready for Epic 5**: ✅ YES - All prerequisites met, zero blockers

---

*This handoff document is part of the BMAD™ Method epic transition framework*
