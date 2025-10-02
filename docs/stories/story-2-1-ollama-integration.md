# Story 2.1: OLLAMA Integration and Model Setup

**Epic:** [Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)

**Status:** ✅ Completed

---

## User Story

As a **backend developer**,
I want **OLLAMA configured with selected LLM model**,
so that **extraction pipeline can perform inference on markdown documents**.

---

## Acceptance Criteria

### AC #1: OLLAMA Service in Docker Configuration ✅
**Status:** Completed (External OLLAMA service)
- OLLAMA service running externally on `http://localhost:11434`
- Docker Compose configuration available in [infrastructure/docker-compose.yml](../../infrastructure/docker-compose.yml) for future deployment
- Environment variable `OLLAMA_BASE_URL` configured in [.env](../../.env)

**Verification:**
```bash
curl http://localhost:11434/api/tags
# Returns available models successfully
```

### AC #2: Model Loaded and Available ✅
**Status:** Completed
- **Extraction Model:** `qwen2.5:7b-instruct-q4_K_M` (7.6B parameters, Q4_K_M quantization)
- **Embedding Model:** `nomic-embed-text:latest` (137M parameters, F16, 768-dimensional output)
- Both models pulled and verified via OLLAMA API

**Verification:**
```bash
curl http://localhost:11434/api/tags | jq '.models[].name'
# Shows: qwen2.5:7b-instruct-q4_K_M, nomic-embed-text:latest
```

### AC #3: Python Client Library Installed ✅
**Status:** Completed
- Added `ollama>=0.3.0` to [apps/api/requirements.txt](../../apps/api/requirements.txt:L8)
- Client configured to communicate with OLLAMA service at configured host

### AC #4: Extraction Service Class with OLLAMA Integration ✅
**Status:** Completed
- Created [apps/api/src/services/ollama_service.py](../../apps/api/src/services/ollama_service.py)
- Service class `OllamaService` with configuration via `OllamaConfig` Pydantic model
- `generate()` method sends prompt + document text to OLLAMA and receives response
- Supports optional system prompts and JSON-formatted responses
- Returns structured response with content, model info, timing metadata

**Key Features:**
- Async/await pattern with `asyncio.to_thread()` wrapper for sync OLLAMA client
- Configurable via Pydantic `OllamaConfig` (host, model, timeout, retries)
- Type-safe response structure with metadata (duration, eval counts, etc.)

### AC #5: Retry Logic with Exponential Backoff ✅
**Status:** Completed
- Implemented in `OllamaService.generate()` method
- Configurable `max_retries` (default: 3 attempts)
- Exponential backoff: delay = `retry_delay * (2 ** attempt)` (default: 1s, 2s, 4s)
- Handles both timeout errors and general exceptions
- Logs warnings on retry attempts with attempt counter

**Retry Behavior:**
1. First attempt fails → wait 1s
2. Second attempt fails → wait 2s
3. Third attempt fails → raise exception with details

### AC #6: Timeout Handling ✅
**Status:** Completed
- Default timeout: 30 seconds per document (configurable via `OllamaConfig.timeout`)
- Uses `asyncio.wait_for()` to enforce timeout on blocking OLLAMA calls
- Timeout errors logged and trigger retry logic
- Clear error messages indicate timeout duration

### AC #7: Health Check Endpoint ✅
**Status:** Completed
- Added OLLAMA health check to [apps/api/src/main.py](../../apps/api/src/main.py:L37-L64)
- Endpoint: `GET /api/health`
- Verifies:
  1. OLLAMA service is responding
  2. Configured model is loaded and available
  3. Test inference succeeds (sends "Respond with 'OK'" prompt)
- Returns health status, model name, available models list, timestamp

**Response Structure:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-03T00:00:00Z",
  "database": "connected",
  "ollama": {
    "status": "healthy",
    "model": "qwen2.5:7b-instruct-q4_K_M",
    "model_loaded": true
  }
}
```

### AC #8: Unit Test for Service Integration ✅
**Status:** Completed
- Created [apps/api/tests/test_ollama_service.py](../../apps/api/tests/test_ollama_service.py)
- **11 comprehensive test cases:**
  1. `test_ollama_service_initialization` - Configuration validation
  2. `test_ollama_service_default_config` - Default values
  3. `test_generate_success` - Successful LLM response
  4. `test_generate_with_json_format` - JSON format request
  5. `test_generate_timeout_retry` - Timeout retry logic
  6. `test_generate_retry_with_eventual_success` - Retry with success
  7. `test_health_check_success` - Healthy service verification
  8. `test_health_check_model_not_loaded` - Missing model detection
  9. `test_health_check_service_timeout` - Service timeout handling
  10. `test_health_check_service_error` - Connection error handling
  11. `test_ollama_real_connection` - Integration test (manual only)

**Test Coverage:**
- Service initialization and configuration
- Successful generation with metadata validation
- JSON format request handling
- Timeout and retry mechanisms
- Health check success and failure scenarios
- Real integration test (skipped in CI, run manually with `--run-integration`)

---

## Database Schema (Prerequisite for Story 2.2)

### Migration Created: `f33a8da5c6eb_create_extraction_tables.py` ✅

**Tables Created:**

#### `extracted_stories`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| document_id | UUID | FK documents.id, UNIQUE, ON DELETE CASCADE | Reference to source document |
| role | VARCHAR(500) | NULL | "As a [role]" component |
| action | VARCHAR(1000) | NULL | "I want [action]" component |
| benefit | VARCHAR(1000) | NULL | "So that [benefit]" component |
| acceptance_criteria | JSONB | NULL | Array of AC items |
| status | VARCHAR(50) | NULL | Story status (draft/dev/done) |
| confidence_score | FLOAT | NULL | LLM extraction confidence |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW(), ON UPDATE NOW() | Update timestamp |

**Index:** `idx_extracted_stories_status` on `status` column

#### `extracted_epics`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| document_id | UUID | FK documents.id, UNIQUE, ON DELETE CASCADE | Reference to source document |
| title | VARCHAR(500) | NULL | Epic title |
| goal | TEXT | NULL | Epic goal/description |
| status | VARCHAR(50) | NULL | Epic status (draft/dev/done) |
| related_stories | JSONB | NULL | Array of related story identifiers |
| confidence_score | FLOAT | NULL | LLM extraction confidence |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW(), ON UPDATE NOW() | Update timestamp |

**Index:** `idx_extracted_epics_status` on `status` column

**Migration Applied:** ✅ 2025-10-03
```bash
DATABASE_URL="postgresql+asyncpg://bmadflow:bmadflow_dev@localhost:5434/bmadflow" \
  alembic upgrade head
# Created: extracted_stories, extracted_epics tables with indexes
```

---

## Implementation Details

### Files Created/Modified

**New Files:**
- [apps/api/src/services/ollama_service.py](../../apps/api/src/services/ollama_service.py) - OLLAMA service class (175 lines)
- [apps/api/tests/test_ollama_service.py](../../apps/api/tests/test_ollama_service.py) - Unit tests (11 test cases)
- [apps/api/alembic/versions/f33a8da5c6eb_create_extraction_tables.py](../../apps/api/alembic/versions/f33a8da5c6eb_create_extraction_tables.py) - Database migration

**Modified Files:**
- [apps/api/requirements.txt](../../apps/api/requirements.txt) - Added `ollama>=0.3.0`
- [apps/api/src/main.py](../../apps/api/src/main.py:L37-L64) - Added OLLAMA health check to `/api/health` endpoint

### Service Architecture

```python
# Configuration (Pydantic model)
OllamaConfig(
    host="http://localhost:11434",
    model="qwen2.5:7b-instruct-q4_K_M",
    timeout=30.0,
    max_retries=3,
    retry_delay=1.0
)

# Service usage
service = OllamaService(config)
response = await service.generate(
    prompt="Extract user story components...",
    system_prompt="You are a BMAD document analyzer...",
    format_json=True  # Request JSON-formatted response
)

# Response structure
{
    "content": "...",  # LLM response text
    "model": "qwen2.5:7b-instruct-q4_K_M",
    "created_at": "2025-10-03T00:00:00Z",
    "done": True,
    "total_duration": 1000000,  # nanoseconds
    "prompt_eval_count": 10,
    "eval_count": 20
}
```

---

## Testing

### Unit Tests (Mock-based)
```bash
pytest apps/api/tests/test_ollama_service.py -v
```
All 10 unit tests pass (integration test skipped)

### Manual Integration Test
```bash
pytest apps/api/tests/test_ollama_service.py::test_ollama_real_connection --run-integration
```
Requires OLLAMA running with `qwen2.5:7b-instruct-q4_K_M` model

### Health Check Verification
```bash
curl http://localhost:8000/api/health | jq
```
Expected response includes `"ollama": {"status": "healthy", "model_loaded": true}`

---

## Dependencies

**Prerequisites Met:**
- ✅ Epic 1 Story 1.7: OLLAMA model selected (`qwen2.5:7b-instruct-q4_K_M`)
- ✅ OLLAMA server running on localhost:11434
- ✅ Models pulled and available

**Dependencies for Next Stories:**
- Story 2.2 (User Story Extraction): Requires `extracted_stories` table ✅
- Story 2.3 (Epic Extraction): Requires `extracted_epics` table ✅
- Story 2.4 (Status Detection): Requires status columns in extraction tables ✅

---

## Configuration

### Environment Variables ([.env](../../.env))
```bash
# OLLAMA Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_EXTRACTION_MODEL=qwen2.5:7b-instruct-q4_K_M
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_EMBEDDING_DIMENSION=768
OLLAMA_TIMEOUT=30.0

# Active Provider
LLM_PROVIDER=ollama
```

---

## Next Steps

With Story 2.1 complete, proceed to:

1. **Story 2.2:** Implement user story extraction using `OllamaService`
2. **Story 2.3:** Implement epic extraction and relationship parsing
3. **Story 2.4:** Implement status detection (explicit markers + inference)
4. **Story 2.5:** Integrate extraction pipeline with GitHub sync

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-03 | 1.0 | Story 2.1 completed - OLLAMA integration and database schema | Claude (Dev) |
