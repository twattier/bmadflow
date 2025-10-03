# Story 3.0: Backend API Endpoints for Dashboard Views

**Epic:** Epic 3: Multi-View Documentation Dashboard
**Priority:** Critical (Pre-requisite for all Epic 3 stories)
**Status:** Ready for Development

## User Story

As a **frontend developer**,
I want **REST API endpoints to retrieve documents and extracted data**,
so that **dashboard views can fetch and display content**.

## Context

Epic 3 requires frontend views to display documents, epics, stories, and relationships. This story provides the backend API layer that Epic 1 and Epic 2 have prepared data for, but haven't exposed via HTTP endpoints yet.

**Why This Story Exists:**
- Epic 1 created the `documents` table and sync pipeline
- Epic 2 created `extracted_epics`, `extracted_stories`, and `relationships` tables
- Epic 3 needs to **read** this data via REST APIs
- Without these endpoints, Stories 3.1-3.7 are blocked

## Acceptance Criteria

### AC1: Documents by Type Endpoint
**Endpoint:** `GET /api/projects/{project_id}/documents?type={type}`

**Requirements:**
1. Returns list of documents filtered by `doc_type` (scoping, architecture, epic, story, qa, other)
2. Query parameter `type` is optional (if omitted, returns all documents)
3. Response includes: `id`, `file_path`, `doc_type`, `title`, `excerpt`, `last_modified`, `extraction_status`
4. Documents sorted by `file_path` (alphabetical)
5. Returns 404 if project not found
6. Returns empty array if no documents match filter

**Response Schema:**
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "file_path": "docs/scoping/prd.md",
    "doc_type": "scoping",
    "title": "Product Requirements Document",
    "excerpt": "BMADFlow is a self-hosted dashboard...",
    "last_modified": "2025-10-01T14:32:15Z",
    "extraction_status": "completed",
    "extraction_confidence": 0.95
  }
]
```

### AC2: Single Document Endpoint
**Endpoint:** `GET /api/documents/{document_id}`

**Requirements:**
1. Returns single document with **full content** (not just excerpt)
2. Response includes all document fields: `id`, `project_id`, `file_path`, `content`, `doc_type`, `title`, `excerpt`, `last_modified`, `extraction_status`, `extraction_confidence`
3. Returns 404 if document not found
4. No authentication required (POC - public repos only)

**Response Schema:**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "file_path": "docs/epics/epic-3-multi-view-dashboard.md",
  "content": "# Epic 3: Multi-View Documentation Dashboard\n\n**Status:** Draft\n\n...",
  "doc_type": "epic",
  "title": "Epic 3: Multi-View Documentation Dashboard",
  "excerpt": "Create 4-view dashboard (Scoping, Architecture...",
  "last_modified": "2025-10-01T14:32:15Z",
  "extraction_status": "completed",
  "extraction_confidence": 0.92
}
```

### AC3: Epics List Endpoint
**Endpoint:** `GET /api/epics?project_id={project_id}`

**Requirements:**
1. Returns all epics for a project with extracted metadata
2. Joins `documents` + `extracted_epics` tables
3. Query parameter `project_id` is required (returns 400 if missing)
4. Response includes: epic fields + document title, file_path, last_modified
5. Epics sorted by `epic_number` (ascending)
6. Returns empty array if no epics found

**Response Schema:**
```json
[
  {
    "id": "uuid",
    "document_id": "uuid",
    "epic_number": 1,
    "title": "Foundation, GitHub Integration & Dashboard Shell",
    "goal": "Establish core infrastructure...",
    "status": "done",
    "story_count": 8,
    "confidence_score": 0.95,
    "extracted_at": "2025-10-01T14:32:15Z",
    "document": {
      "file_path": "docs/epics/epic-1-foundation-github-dashboard.md",
      "last_modified": "2025-10-01T14:32:15Z"
    }
  }
]
```

### AC4: Relationships GraphData Endpoint
**Endpoint:** `GET /api/projects/{project_id}/relationships?epic_id={epic_id}`

**Requirements:**
1. Returns epic-story relationship graph in format specified by architecture (`GraphData` interface)
2. Query parameter `epic_id` is optional (if omitted, returns all epics + stories)
3. If `epic_id` provided, returns only that epic and its child stories
4. Joins `extracted_epics`, `extracted_stories`, `relationships`, `documents` tables
5. Returns nodes (epics + stories) and edges (relationships)
6. Returns 404 if project not found, 404 if epic_id specified but not found

**Response Schema:**
```json
{
  "nodes": [
    {
      "id": "uuid",
      "title": "Epic 1: Foundation",
      "type": "epic",
      "status": "done",
      "document_id": "uuid"
    },
    {
      "id": "uuid",
      "title": "Story 1.1: Project Infrastructure Setup",
      "type": "story",
      "status": "done",
      "document_id": "uuid"
    }
  ],
  "edges": [
    {
      "source_id": "epic_uuid",
      "target_id": "story_uuid",
      "type": "contains"
    }
  ]
}
```

### AC5: Document Path Resolution Endpoint
**Endpoint:** `GET /api/documents/resolve?file_path={file_path}&project_id={project_id}`

**Requirements:**
1. Maps file path (e.g., `../architecture.md`, `/docs/epics/epic-1.md`) to document ID
2. Query parameters `file_path` and `project_id` required (returns 400 if missing)
3. Handles relative paths by resolving against project's `/docs` root
4. Returns 404 if document not found (not an error - used for broken link detection)
5. Returns document ID + basic metadata

**Response Schema:**
```json
{
  "id": "uuid",
  "file_path": "docs/architecture.md",
  "title": "BMADFlow Fullstack Architecture Document",
  "doc_type": "architecture"
}
```

### AC6: Unit Tests
1. Each endpoint has pytest test coverage (test_documents_routes.py, test_epics_routes.py, test_relationships_routes.py)
2. Tests cover: success cases, 404 not found, 400 bad request, query parameter filtering
3. Tests use pytest fixtures for database setup (async test DB)
4. All tests pass: `pytest apps/api/tests/test_*_routes.py -v`

### AC7: OpenAPI Documentation
1. FastAPI auto-generates OpenAPI spec at `/docs`
2. All endpoints documented with description, parameters, response schemas
3. Manual verification: Visit `http://localhost:8000/docs` and test each endpoint via Swagger UI

### AC8: Integration with Existing Code
1. New route files created: `apps/api/src/routes/documents.py`, `apps/api/src/routes/epics.py`
2. Routes registered in `apps/api/src/main.py`
3. Repositories extended if needed (DocumentRepository, EpicRepository, StoryRepository, RelationshipRepository)
4. No breaking changes to existing Epic 1/2 code

## Technical Implementation Notes

### Suggested Approach

**1. Create Route Files:**
- `apps/api/src/routes/documents.py` - AC1, AC2, AC5
- `apps/api/src/routes/epics.py` - AC3
- `apps/api/src/routes/relationships.py` - AC4

**2. Extend Repositories (if needed):**
- `DocumentRepository.get_by_type(project_id, doc_type)` - AC1
- `DocumentRepository.get_by_id(document_id)` - AC2 (may already exist)
- `DocumentRepository.resolve_path(project_id, file_path)` - AC5
- `EpicRepository.get_by_project(project_id)` - AC3 (with join)
- `RelationshipRepository.get_graph_data(project_id, epic_id?)` - AC4

**3. Create Pydantic Schemas:**
- `apps/api/src/schemas/document.py` - DocumentListResponse, DocumentDetailResponse
- `apps/api/src/schemas/epic.py` - EpicListResponse
- `apps/api/src/schemas/relationship.py` - GraphDataResponse, NodeSchema, EdgeSchema

**4. Register Routes:**
```python
# apps/api/src/main.py
from .routes import documents, epics, relationships

app.include_router(documents.router, prefix="/api")
app.include_router(epics.router, prefix="/api")
app.include_router(relationships.router, prefix="/api")
```

### File Path Resolution Logic (AC5)

**Challenge:** Markdown links can be:
- Relative: `../architecture.md`, `./story-1-1.md`
- Absolute: `/docs/epics/epic-1.md`
- Partial: `epic-1.md`

**Solution:**
```python
def resolve_file_path(project_id: uuid.UUID, file_path: str) -> str:
    """Resolve relative/absolute paths to normalized file_path in DB."""
    # Remove leading slash
    normalized = file_path.lstrip('/')

    # If relative path (../, ./), assume context is /docs/
    if normalized.startswith('../'):
        normalized = normalized.replace('../', '')
    if normalized.startswith('./'):
        normalized = normalized.replace('./', '')

    # Ensure path starts with 'docs/'
    if not normalized.startswith('docs/'):
        normalized = f'docs/{normalized}'

    return normalized
```

Query DB: `SELECT * FROM documents WHERE project_id = ? AND file_path = ?`

## Definition of Done

- [ ] All 8 acceptance criteria met
- [ ] 5 endpoints implemented and functional
- [ ] Unit tests written and passing (pytest)
- [ ] OpenAPI docs generated and verified
- [ ] Code reviewed and merged to main
- [ ] Manual testing completed via Swagger UI
- [ ] No breaking changes to Epic 1/2 code
- [ ] Frontend dev can call endpoints and receive expected data

## Estimated Effort

**4-6 hours** (1 day for careful implementation + testing)

**Breakdown:**
- Route implementation: 2-3 hours
- Repository extensions: 1 hour
- Pydantic schemas: 30 minutes
- Unit tests: 1.5-2 hours
- Manual testing + fixes: 30 minutes

## Dependencies

**Upstream:**
- ✅ Epic 1 Story 1.2: Database schema exists
- ✅ Epic 1 Story 1.4: Sync pipeline populates documents table
- ✅ Epic 2 Stories 2.2-2.3: Extraction tables populated (extracted_epics, extracted_stories)
- ✅ Epic 2 Story 2.3: Relationships table populated

**Downstream (Blocks):**
- 🔴 Story 3.1: Scoping View (needs AC1)
- 🔴 Story 3.2: Detail View (needs AC2)
- 🔴 Story 3.4: Architecture View (needs AC1)
- 🔴 Story 3.6: Epics View (needs AC3, AC4)
- 🔴 Story 3.7: Inter-Document Links (needs AC5)

## Test Plan

### Unit Tests (AC6)

**File:** `apps/api/tests/test_documents_routes.py`
```python
@pytest.mark.asyncio
async def test_get_documents_by_type(client: AsyncClient, db_session):
    # Test AC1: Filter by type
    response = await client.get("/api/projects/{project_id}/documents?type=epic")
    assert response.status_code == 200
    assert all(doc["doc_type"] == "epic" for doc in response.json())

@pytest.mark.asyncio
async def test_get_document_by_id(client: AsyncClient, db_session):
    # Test AC2: Single document
    response = await client.get("/api/documents/{document_id}")
    assert response.status_code == 200
    assert "content" in response.json()

@pytest.mark.asyncio
async def test_resolve_document_path(client: AsyncClient, db_session):
    # Test AC5: Path resolution
    response = await client.get("/api/documents/resolve?file_path=../epic-1.md&project_id={id}")
    assert response.status_code == 200
```

### Manual Testing (AC7)

1. Start backend: `docker compose up api`
2. Visit: `http://localhost:8000/docs`
3. Test each endpoint via Swagger UI
4. Verify responses match schemas

## Success Criteria

**Story is complete when:**
1. All 5 endpoints return correct data
2. All unit tests pass
3. Frontend developer can integrate endpoints into React components
4. Epic 3 Stories 3.1-3.7 are unblocked

## Notes

- This is a **pre-requisite story** - must complete before other Epic 3 stories
- No UI work required (backend only)
- Reuses existing database schema and repositories from Epic 1/2
- Should be straightforward implementation (mostly CRUD endpoints)

---

**Story Created:** 2025-10-03
**Created By:** Claude (PM)
**Target Start:** Immediately (Epic 3 blocker)
**Target Completion:** 1 day
