# API Specification

**Base URL:** `http://localhost:8000/api` (development), `https://bmadflow.internal/api` (production)

**Authentication:** None for POC (public repos only). Phase 2: JWT Bearer token.

## Key Endpoints

### Projects

- `POST /projects` - Create new project
  - Request: `{github_url: string}`
  - Response: `201 Created` with `Project`

- `GET /projects` - List all projects
  - Response: `200 OK` with `Project[]`

- `GET /projects/{id}` - Get project by ID
  - Response: `200 OK` with `Project`

- `POST /projects/{id}/sync` - Trigger manual sync
  - Response: `202 Accepted` with `{sync_task_id: string, message: string}`

- `GET /projects/{id}/sync-status` - Get sync status
  - Response: `200 OK` with `{status: string, processed_count: int, total_count: int, error_message: string | null, retry_allowed: boolean}`

### Documents

- `GET /projects/{id}/documents?type={scoping|architecture|epic|story}` - Get documents by type
  - Response: `200 OK` with `Document[]`

- `GET /documents/{id}` - Get single document with full content
  - Response: `200 OK` with `Document`

### Epics & Stories

- `GET /projects/{id}/relationships?epic_id={id}` - Get epic-story graph data
  - Response: `200 OK` with `GraphData`

- `GET /epics?project_id={id}` - Get all epics
  - Response: `200 OK` with `ExtractedEpic[]`

- `GET /stories?project_id={id}&epic_id={id}` - Get stories
  - Response: `200 OK` with `ExtractedStory[]`

### Feedback

- `POST /feedback` - Submit pilot user feedback (Story 4.7)
  - Request: `{project_id: string, rating: int (1-5), better_than_github: boolean, favorite_feature?: string, improvement_suggestions?: string}`
  - Response: `201 Created`

### Health Check

- `GET /health` - Health check
  - Response: `200 OK` with `{status: "ok", ollama_status: "ok"}`

## Error Response Format

All errors follow consistent structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {},
    "timestamp": "2025-10-01T14:32:15Z",
    "requestId": "uuid"
  }
}
```

Common error codes: `PROJECT_NOT_FOUND`, `INVALID_GITHUB_URL`, `SYNC_IN_PROGRESS`, `GITHUB_RATE_LIMIT`, `VALIDATION_ERROR`

---
