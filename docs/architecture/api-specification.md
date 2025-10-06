# API Specification

## Overview

BMADFlow provides a **RESTful API** built with **FastAPI** that follows OpenAPI 3.0 specifications. All endpoints are prefixed with `/api/` and return JSON responses. The API supports CRUD operations for projects, project docs, documents, conversations, and vector search functionality.

**API Design Principles:**
- **REST Conventions**: Standard HTTP verbs (GET, POST, PUT, DELETE) with appropriate status codes
- **Resource-Based URLs**: Endpoints organized by resource type (projects, documents, conversations)
- **Consistent Responses**: All responses follow standard JSON structure with Pydantic validation
- **OpenAPI Documentation**: Auto-generated interactive docs at `/api/docs` (Swagger UI) and `/api/redoc`
- **Error Handling**: Standardized error responses with detail messages

**Base URL**: `http://localhost:8000/api` (configurable via BACKEND_PORT env var)

**Authentication**: None for POC (single-tenant, localhost only)

---

## API Endpoints Summary

| Resource | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| **Health** | GET | `/api/health` | Health check with database status |
| **Projects** | GET | `/api/projects` | List all projects |
| **Projects** | POST | `/api/projects` | Create new project |
| **Projects** | GET | `/api/projects/{id}` | Get project by ID |
| **Projects** | PUT | `/api/projects/{id}` | Update project |
| **Projects** | DELETE | `/api/projects/{id}` | Delete project |
| **Project Docs** | GET | `/api/projects/{id}/project-docs` | List project docs for project |
| **Project Docs** | POST | `/api/projects/{id}/project-docs` | Create project doc |
| **Project Docs** | GET | `/api/project-docs/{id}` | Get project doc by ID |
| **Project Docs** | PUT | `/api/project-docs/{id}` | Update project doc |
| **Project Docs** | DELETE | `/api/project-docs/{id}` | Delete project doc |
| **Project Docs** | POST | `/api/project-docs/{id}/sync` | Trigger GitHub sync |
| **Project Docs** | GET | `/api/project-docs/{id}/sync-status` | Get sync status |
| **Documents** | GET | `/api/projects/{id}/file-tree` | Get hierarchical file tree |
| **Documents** | GET | `/api/documents/{id}` | Get document content |
| **Search** | POST | `/api/projects/{id}/search` | Vector similarity search |
| **LLM Providers** | GET | `/api/llm-providers` | List LLM providers |
| **LLM Providers** | POST | `/api/llm-providers` | Create LLM provider |
| **LLM Providers** | PUT | `/api/llm-providers/{id}` | Update LLM provider |
| **LLM Providers** | DELETE | `/api/llm-providers/{id}` | Delete LLM provider |
| **LLM Providers** | PUT | `/api/llm-providers/{id}/set-default` | Set as default |
| **Conversations** | GET | `/api/projects/{id}/conversations` | List conversations for project |
| **Conversations** | POST | `/api/projects/{id}/conversations` | Create new conversation |
| **Conversations** | GET | `/api/conversations/{id}` | Get conversation with messages |
| **Conversations** | DELETE | `/api/conversations/{id}` | Delete conversation |
| **Messages** | POST | `/api/conversations/{id}/messages` | Send message, get AI response |

---

## Detailed Endpoint Specifications

### Health Check

**`GET /api/health`**

Health check endpoint for monitoring and startup validation.

**Response 200**:
```json
{
  "status": "ok",
  "database": "connected",
  "ollama": "connected",
  "version": "1.0.0"
}
```

**Response 503** (if database or Ollama unavailable):
```json
{
  "status": "degraded",
  "database": "disconnected",
  "ollama": "disconnected"
}
```

**Requirements**: FR32 (validate Ollama availability on startup)

---

### Projects API

**`GET /api/projects`**

List all projects with basic metadata.

**Response 200**:
```json
[
  {
    "id": "uuid",
    "name": "BMAD Method",
    "description": "Business Modeling & Architecture Design",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
]
```

---

**`POST /api/projects`**

Create a new project.

**Request Body** (`ProjectCreate`):
```json
{
  "name": "BMAD Method",
  "description": "Business Modeling & Architecture Design"
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "name": "BMAD Method",
  "description": "Business Modeling & Architecture Design",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Response 400** (validation error):
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Requirements**: Story 2.1

---

**`GET /api/projects/{id}`**

Get project by ID.

**Response 200**: Same as POST response

**Response 404**:
```json
{
  "detail": "Project not found"
}
```

---

**`PUT /api/projects/{id}`**

Update project (partial update supported).

**Request Body** (`ProjectUpdate`):
```json
{
  "name": "BMAD Method v2",
  "description": "Updated description"
}
```

**Response 200**: Updated project object

---

**`DELETE /api/projects/{id}`**

Delete project (cascades to project_docs and conversations).

**Response 204**: No content

**Response 404**: Project not found

---

### Project Docs API

**`GET /api/projects/{id}/project-docs`**

List all project docs for a project.

**Response 200**:
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "name": "Core Documentation",
    "description": "Main BMAD docs",
    "github_url": "https://github.com/user/repo",
    "github_folder_path": "docs",
    "last_synced_at": "2025-01-15T12:00:00Z",
    "last_github_commit_date": "2025-01-15T11:50:00Z",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T12:00:00Z"
  }
]
```

**Requirements**: Story 2.2

---

**`POST /api/projects/{id}/project-docs`**

Create project doc linked to project.

**Request Body** (`ProjectDocCreate`):
```json
{
  "name": "Core Documentation",
  "description": "Main BMAD docs",
  "github_url": "https://github.com/user/repo",
  "github_folder_path": "docs"
}
```

**Response 201**: ProjectDoc object

---

**`POST /api/project-docs/{id}/sync`**

Trigger GitHub sync for project doc.

**Response 202** (Accepted - async processing):
```json
{
  "message": "Sync started",
  "project_doc_id": "uuid",
  "status": "processing"
}
```

**Processing Steps** (FR23, Story 2.5):
1. Fetch GitHub repository tree
2. Download supported files (.md, .csv, .yaml, .json)
3. Store in documents table (upsert)
4. Process with Docling → generate embeddings → store in chunks table
5. Update last_synced_at timestamp

**Performance**: NFR3 (sync+indexing completes in <5 minutes per ProjectDoc)

---

**`GET /api/project-docs/{id}/sync-status`**

Get current sync status.

**Response 200**:
```json
{
  "project_doc_id": "uuid",
  "status": "syncing",
  "progress": "Processing file 5 of 10",
  "last_synced_at": "2025-01-15T12:00:00Z"
}
```

**Status Values**: `not_synced`, `syncing`, `synced`, `error`

---

### Documents & File Tree API

**`GET /api/projects/{id}/file-tree`**

Get hierarchical file tree structure.

**Response 200**:
```json
{
  "project_id": "uuid",
  "tree": [
    {
      "type": "folder",
      "name": "docs",
      "path": "docs",
      "children": [
        {
          "type": "file",
          "id": "uuid",
          "name": "architecture.md",
          "path": "docs/architecture.md",
          "file_type": "md",
          "size": 45000
        }
      ]
    }
  ]
}
```

**Requirements**: Story 3.1

---

**`GET /api/documents/{id}`**

Get document content and metadata.

**Response 200**:
```json
{
  "id": "uuid",
  "project_doc_id": "uuid",
  "file_path": "docs/architecture.md",
  "file_type": "md",
  "file_size": 45000,
  "content": "# Architecture\n\n...",
  "metadata": {
    "headers": ["Introduction", "High Level Architecture"]
  },
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

**Requirements**: Story 3.3

---

### Vector Search API

**`POST /api/projects/{id}/search`**

Perform vector similarity search scoped to project.

**Request Body**:
```json
{
  "query": "How does the RAG pipeline work?",
  "top_k": 5,
  "similarity_threshold": 0.7
}
```

**Response 200**:
```json
{
  "query": "How does the RAG pipeline work?",
  "results": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "chunk_text": "The RAG pipeline integrates Docling for document processing...",
      "header_anchor": "#rag-pipeline",
      "similarity_score": 0.89,
      "file_path": "docs/architecture.md"
    }
  ]
}
```

**Processing**:
1. Generate embedding for query using Ollama (nomic-embed-text)
2. Perform pgvector similarity search with cosine distance
3. Filter by project_id
4. Return top-k results with similarity scores

**Performance**: NFR4 (<500ms search time)

**Requirements**: Story 4.6

---

### LLM Providers API

**`GET /api/llm-providers`**

List configured LLM providers.

**Response 200**:
```json
[
  {
    "id": "uuid",
    "provider_name": "ollama",
    "model_name": "llama2",
    "is_default": true,
    "api_config": {
      "base_url": "http://localhost:11434",
      "temperature": 0.7
    },
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

---

**`POST /api/llm-providers`**

Create LLM provider configuration.

**Request Body**:
```json
{
  "provider_name": "openai",
  "model_name": "gpt-4",
  "is_default": false,
  "api_config": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**Response 201**: LLMProvider object

**Note**: API keys stored in .env, NOT in api_config

**Requirements**: Story 5.1

---

**`PUT /api/llm-providers/{id}/set-default`**

Set provider as default (unsets other defaults).

**Response 200**: Updated LLMProvider object

---

### Conversations & Messages API

**`GET /api/projects/{id}/conversations`**

List recent conversations for project (last 10).

**Response 200**:
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "llm_provider_id": "uuid",
    "title": "RAG Pipeline Questions",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T12:00:00Z"
  }
]
```

---

**`POST /api/projects/{id}/conversations`**

Create new conversation.

**Request Body** (`ConversationCreate`):
```json
{
  "llm_provider_id": "uuid",
  "title": "RAG Pipeline Questions"
}
```

**Response 201**: Conversation object

**Requirements**: Story 5.3

---

**`GET /api/conversations/{id}`**

Get conversation with all messages.

**Response 200**:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "llm_provider_id": "uuid",
  "title": "RAG Pipeline Questions",
  "messages": [
    {
      "id": "uuid",
      "conversation_id": "uuid",
      "role": "user",
      "content": "How does the RAG pipeline work?",
      "sources": null,
      "created_at": "2025-01-15T12:00:00Z"
    },
    {
      "id": "uuid",
      "conversation_id": "uuid",
      "role": "assistant",
      "content": "The RAG pipeline in BMADFlow works as follows...",
      "sources": [
        {
          "document_id": "uuid",
          "file_path": "docs/architecture.md",
          "header_anchor": "#rag-pipeline",
          "similarity_score": 0.89
        }
      ],
      "created_at": "2025-01-15T12:00:05Z"
    }
  ],
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T12:00:05Z"
}
```

---

**`POST /api/conversations/{id}/messages`**

Send message and get AI response.

**Request Body** (`MessageCreate`):
```json
{
  "content": "How does the RAG pipeline work?"
}
```

**Response 201**:
```json
{
  "user_message": {
    "id": "uuid",
    "role": "user",
    "content": "How does the RAG pipeline work?",
    "created_at": "2025-01-15T12:00:00Z"
  },
  "assistant_message": {
    "id": "uuid",
    "role": "assistant",
    "content": "The RAG pipeline in BMADFlow works as follows...",
    "sources": [
      {
        "document_id": "uuid",
        "file_path": "docs/architecture.md",
        "header_anchor": "#rag-pipeline",
        "similarity_score": 0.89
      }
    ],
    "created_at": "2025-01-15T12:00:05Z"
  }
}
```

**Processing** (Pydantic Agent Framework - Story 5.2):
1. Store user message
2. Generate query embedding
3. Perform vector search (top-k chunks)
4. Call LLM with context (RAG)
5. Format response with source attribution
6. Store assistant message with sources
7. Return both messages

**Performance**:
- NFR2: <3s response time (cloud LLMs), <10s (Ollama)
- NFR4: <500ms vector search component

---

## OpenAPI Documentation

**Interactive Documentation**: `http://localhost:8000/api/docs` (Swagger UI)

**ReDoc**: `http://localhost:8000/api/redoc`

**OpenAPI JSON**: `http://localhost:8000/api/openapi.json`

**Auto-Generated from**:
- FastAPI route definitions
- Pydantic request/response models
- Docstrings and descriptions

**Requirements**: FR30 (OpenAPI/Swagger documentation)

---

## Error Response Format

All errors follow consistent JSON structure:

**Validation Error (422)**:
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Not Found (404)**:
```json
{
  "detail": "Project not found"
}
```

**Internal Server Error (500)**:
```json
{
  "detail": "Internal server error",
  "error_code": "DATABASE_ERROR"
}
```

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT requests |
| 201 | Created | Successful POST request |
| 202 | Accepted | Async operation started (sync) |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid request data |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Database/Ollama unavailable |

---

## CORS Configuration

**Allowed Origins** (development):
- `http://localhost:3000` (frontend dev server)

**Production**: Configure via ALLOWED_ORIGINS environment variable

**Implementation**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## API Client (Frontend Integration)

**Axios Configuration Example**:
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Example: List projects
const getProjects = async (): Promise<ProjectResponse[]> => {
  const response = await apiClient.get<ProjectResponse[]>('/projects');
  return response.data;
};

// Example: Send chat message
const sendMessage = async (
  conversationId: string,
  content: string
): Promise<MessageResponse> => {
  const response = await apiClient.post<MessageResponse>(
    `/conversations/${conversationId}/messages`,
    { content }
  );
  return response.data;
};
```

---

## Related Documentation

- **Data Models**: See [Data Models](#data-models) section for Pydantic request/response schemas
- **Backend Architecture**: See [Backend Architecture](#backend-architecture) section for service layer implementation
- **Implementation Patterns**: [FastAPI Patterns](context/backend/fastapi-patterns.md) for route examples

---

