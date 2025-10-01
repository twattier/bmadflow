# BMADFlow Fullstack Architecture Document

## Introduction

This document outlines the complete fullstack architecture for **BMADFlow**, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

### Starter Template or Existing Project

**N/A - Greenfield project** with manual setup following PRD specifications. This approach provides maximum clarity for AI-assisted development and avoids starter template constraints.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Initial architecture document created from PRD and front-end spec | Winston (Architect) |
| 2025-10-01 | 1.1 | Updated to reference extracted epic and story files | Sarah (PO) |

---

## High Level Architecture

### Technical Summary

BMADFlow is a **modular monolithic SPA + API architecture** deployed via Docker Compose for the POC. The frontend is a React 18+ SPA built with Vite, using shadcn/ui components and React Router for the 4-view dashboard (Scoping, Architecture, Epics, Detail). The backend is a Python FastAPI application with PostgreSQL 15+ (using pgvector for future semantic search) and Redis for caching, integrated with your existing external OLLAMA server for LLM-powered markdown extraction.

The monorepo structure (npm workspaces) enables shared TypeScript interfaces between frontend and backend. Key integration points include RESTful JSON APIs with WebSocket support for real-time sync progress, GitHub API integration for repository fetching, and OLLAMA inference for extracting BMAD-structured content.

Infrastructure runs entirely on self-hosted servers to maintain documentation privacy. This architecture achieves the PRD's 4-6 week POC timeline by balancing functional completeness (90%+ LLM accuracy, 80% navigation time reduction) with pragmatic simplicity.

### Platform and Infrastructure Choice

**Platform:** Self-hosted on project infrastructure (internal/on-prem servers)

**Key Services:**
- **Frontend:** Nginx serving React SPA static build
- **Backend API:** FastAPI + uvicorn (ASGI server)
- **Database:** PostgreSQL 15+ with pgvector extension
- **Cache:** Redis 7+
- **LLM Inference:** External OLLAMA server (existing GPU-enabled server with Llama 3 8B or Mistral 7B, selected via Story 1.7 benchmarking)
- **Reverse Proxy:** Nginx (single entry point for frontend + API)

**Deployment Host and Regions:** Single-region deployment on project infrastructure. OLLAMA runs on existing external GPU server, accessed via HTTP API.

**Rationale:** Self-hosted Docker Compose provides complete control and no cloud costs. External OLLAMA server ensures privacy compliance and leverages existing GPU infrastructure. Architecture designed for cloud migration in Phase 2 (Kubernetes on AWS/GCP).

### Repository Structure

**Structure:** Monorepo (single Git repository)

**Monorepo Tool:** npm workspaces (simplest for 1 developer + AI)

**Package Organization:**
- `apps/web/` - React frontend SPA
- `apps/api/` - FastAPI backend application
- `packages/shared/` - Shared TypeScript types and constants
- `packages/config/` - Shared ESLint, TypeScript, Prettier configs
- `infrastructure/` - Docker Compose, deployment scripts
- `docs/` - Project documentation

### High Level Architecture Diagram

```mermaid
graph TB
    User[User Browser] --> Nginx[Nginx Reverse Proxy<br/>Port 80/443]

    Nginx --> Frontend[React SPA<br/>Static Files<br/>Port 3000]
    Nginx --> API[FastAPI Backend<br/>Port 8000]

    API --> PG[(PostgreSQL 15+<br/>pgvector<br/>Port 5432)]
    API --> Redis[(Redis Cache<br/>Port 6379)]
    API --> GitHub[GitHub REST API v3<br/>External]

    Frontend -.WebSocket.-> API

    subgraph "Docker Compose Network"
        Frontend
        API
        PG
        Redis
        Nginx
    end

    subgraph "External Infrastructure"
        OLLAMA[OLLAMA Server<br/>GPU-Enabled<br/>Existing]
    end

    API --> OLLAMA
```

### Architectural Patterns

- **Modular Monolith (Backend):** Single FastAPI application with modular services - simpler deployment and debugging for POC
- **Single Page Application (Frontend):** React SPA with client-side routing and lazy-loaded route components
- **Repository Pattern (Backend):** Abstract database access behind repository classes for testability and flexibility
- **API Gateway Pattern:** Single Nginx reverse proxy simplifies CORS and provides centralized SSL termination
- **Backend for Frontend (Implicit):** FastAPI endpoints tailored to frontend needs, reducing frontend transformation logic
- **Component-Based UI (Frontend):** Reusable React components with TypeScript, shadcn/ui as base library
- **Service Layer Pattern (Backend):** Business logic in service classes separate from API route handlers

---

## Tech Stack

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| **Frontend Language** | TypeScript | 5.2+ | Type-safe frontend code | Industry standard, catches errors at compile time |
| **Frontend Framework** | React | 18.2+ | UI component framework | Mature ecosystem, shadcn/ui compatibility |
| **Build Tool** | Vite | 5.0+ | Fast development builds | 10x faster HMR than Webpack |
| **UI Component Library** | shadcn/ui | Latest | Accessible React components | Built on Radix UI (WCAG AA), Tailwind CSS |
| **CSS Framework** | Tailwind CSS | 3.4+ | Utility-first styling | Required by shadcn/ui |
| **State Management** | React Query | 5.0+ | Server state management | Handles API caching, loading states elegantly |
| **State Management** | React Context API | Built-in | UI state | Simple for POC |
| **Routing** | React Router | 6.20+ | Client-side routing | De facto standard for React SPAs |
| **Markdown Rendering** | react-markdown | 9.0+ | Render markdown | Wide plugin ecosystem |
| **Diagram Rendering** | Mermaid.js | 10.6+ | Render diagrams | Supports flowchart, sequence, C4 |
| **Syntax Highlighting** | Prism.js | 2.8+ | Code blocks | Lightweight |
| **Icons** | Lucide Icons | Latest | UI iconography | React-optimized, used by shadcn/ui |
| **Frontend Testing** | Vitest | 1.0+ | Unit testing | Vite-native, faster than Jest |
| **Backend Language** | Python | 3.11+ | Backend code | FastAPI requirement, excellent async |
| **Backend Framework** | FastAPI | 0.104+ | REST API framework | Auto OpenAPI docs, async-first |
| **ASGI Server** | uvicorn | 0.24+ | ASGI web server | Production-ready, WebSocket support |
| **API Style** | REST (JSON) | OpenAPI 3.0 | API communication | PRD requirement, FastAPI auto-generates spec |
| **Database** | PostgreSQL | 15.4+ | Primary data store | Mature, pgvector for future search |
| **Database Extension** | pgvector | 0.5+ | Vector embeddings | Future semantic search |
| **Database Migrations** | Alembic | 1.12+ | Schema migrations | Standard for FastAPI |
| **ORM** | SQLAlchemy | 2.0+ | Database ORM | Async support, type-safe queries |
| **Cache** | Redis | 7.2+ | API response caching | Fast, 5-min TTL |
| **LLM Framework** | Pydantic AI | 0.0.13+ | Structured LLM output | Enforces JSON schema |
| **LLM Inference** | OLLAMA | 0.1.17+ | Self-hosted LLM | Privacy, GPU acceleration |
| **GitHub API Client** | PyGithub | 2.1+ | GitHub REST API | Mature, handles auth |
| **Backend Testing** | pytest | 7.4+ | Unit/integration tests | Python standard, async support |
| **Linting** | ESLint + Prettier | 8.0+/3.0+ | Frontend quality | TypeScript + React rules |
| **Linting** | Black + Ruff | 23.0+/0.1+ | Python quality | Opinionated formatter + fast linter |
| **Containerization** | Docker | 24.0+ | Application containers | Multi-stage builds |
| **Orchestration** | Docker Compose | 2.21+ | Local orchestration | POC deployment |
| **CI/CD** | GitHub Actions | Latest | Automated testing | Free for public repos |
| **Error Tracking** | Sentry | 1.35+ | Error logging | Excellent SDKs, free tier |

---

## Data Models

### Project

Represents a GitHub repository project synced into BMADFlow.

**Key Attributes:**
- `id`: UUID - Primary key
- `name`: string - Project name
- `github_url`: string - Full GitHub repository URL
- `last_sync_timestamp`: datetime
- `sync_status`: enum (`idle`, `syncing`, `error`)
- `sync_progress`: JSON - `{processed: int, total: int, current_file: string}`
- `created_at`: datetime
- `updated_at`: datetime

**TypeScript Interface:**
```typescript
interface Project {
  id: string; // UUID
  name: string;
  github_url: string;
  last_sync_timestamp: string | null;
  sync_status: 'idle' | 'syncing' | 'error';
  sync_progress: { processed: number; total: number; current_file?: string; } | null;
  created_at: string;
  updated_at: string;
}
```

**Relationships:** Has many `Document`

---

### Document

Represents a single markdown file from GitHub repository.

**Key Attributes:**
- `id`: UUID
- `project_id`: UUID (FK)
- `file_path`: string
- `content`: TEXT
- `doc_type`: enum (`scoping`, `architecture`, `epic`, `story`, `qa`, `other`)
- `title`: string
- `excerpt`: string
- `last_modified`: datetime
- `embedding`: vector(384) (Phase 2)
- `extraction_status`: enum (`pending`, `processing`, `completed`, `failed`)
- `extraction_confidence`: float (0.0-1.0)
- `created_at`: datetime

**TypeScript Interface:**
```typescript
interface Document {
  id: string;
  project_id: string;
  file_path: string;
  content: string;
  doc_type: 'scoping' | 'architecture' | 'epic' | 'story' | 'qa' | 'other';
  title: string;
  excerpt: string;
  last_modified: string;
  extraction_status: 'pending' | 'processing' | 'completed' | 'failed';
  extraction_confidence: number;
  created_at: string;
}
```

**Relationships:** Belongs to `Project`, has one `ExtractedEpic` or `ExtractedStory`

---

### ExtractedEpic

Stores LLM-extracted structured data from epic markdown documents.

**Key Attributes:**
- `id`: UUID
- `document_id`: UUID (FK, one-to-one)
- `epic_number`: int
- `title`: string
- `goal`: TEXT
- `status`: enum (`draft`, `dev`, `done`)
- `story_count`: int
- `confidence_score`: float
- `extracted_at`: datetime

**TypeScript Interface:**
```typescript
interface ExtractedEpic {
  id: string;
  document_id: string;
  epic_number: number;
  title: string;
  goal: string;
  status: 'draft' | 'dev' | 'done';
  story_count: number;
  confidence_score: number;
  extracted_at: string;
}
```

**Relationships:** Belongs to `Document`, has many `ExtractedStory`

---

### ExtractedStory

Stores LLM-extracted user story components.

**Key Attributes:**
- `id`: UUID
- `document_id`: UUID (FK, one-to-one)
- `story_number`: string (e.g., "1.1", "2.3a")
- `role`: string
- `action`: TEXT
- `benefit`: TEXT
- `acceptance_criteria`: JSONB (array of strings)
- `status`: enum (`draft`, `dev`, `done`)
- `confidence_score`: float
- `extracted_at`: datetime

**TypeScript Interface:**
```typescript
interface ExtractedStory {
  id: string;
  document_id: string;
  story_number: string;
  role: string;
  action: string;
  benefit: string;
  acceptance_criteria: string[];
  status: 'draft' | 'dev' | 'done';
  confidence_score: number;
  extracted_at: string;
}
```

**Relationships:** Belongs to `Document` and `ExtractedEpic`

---

### Relationship

Models relationships between documents (epic → story).

**Key Attributes:**
- `id`: UUID
- `parent_doc_id`: UUID (FK)
- `child_doc_id`: UUID (FK)
- `relationship_type`: enum (`contains`, `relates_to`, `depends_on`)
- `created_at`: datetime

**TypeScript Interface:**
```typescript
interface Relationship {
  id: string;
  parent_doc_id: string;
  child_doc_id: string;
  relationship_type: 'contains' | 'relates_to' | 'depends_on';
  created_at: string;
}

interface GraphData {
  nodes: Array<{
    id: string;
    title: string;
    type: 'epic' | 'story';
    status: 'draft' | 'dev' | 'done';
    document_id: string;
  }>;
  edges: Array<{
    source_id: string;
    target_id: string;
    type: 'contains' | 'relates_to';
  }>;
}
```

---

## API Specification

**Base URL:** `http://localhost:8000/api` (development), `https://bmadflow.internal/api` (production)

**Authentication:** None for POC (public repos only). Phase 2: JWT Bearer token.

### Key Endpoints

#### Projects

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

#### Documents

- `GET /projects/{id}/documents?type={scoping|architecture|epic|story}` - Get documents by type
  - Response: `200 OK` with `Document[]`

- `GET /documents/{id}` - Get single document with full content
  - Response: `200 OK` with `Document`

#### Epics & Stories

- `GET /projects/{id}/relationships?epic_id={id}` - Get epic-story graph data
  - Response: `200 OK` with `GraphData`

- `GET /epics?project_id={id}` - Get all epics
  - Response: `200 OK` with `ExtractedEpic[]`

- `GET /stories?project_id={id}&epic_id={id}` - Get stories
  - Response: `200 OK` with `ExtractedStory[]`

#### Feedback

- `POST /feedback` - Submit pilot user feedback (Story 4.7)
  - Request: `{project_id: string, rating: int (1-5), better_than_github: boolean, favorite_feature?: string, improvement_suggestions?: string}`
  - Response: `201 Created`

#### Health Check

- `GET /health` - Health check
  - Response: `200 OK` with `{status: "ok", ollama_status: "ok"}`

### Error Response Format

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

## Components Architecture

### Frontend Components

**Core Components:**

1. **DocumentCard** - Reusable card for document previews (Scoping/Architecture views)
   - Dependencies: shadcn/ui Card, StatusBadge, Lucide Icons
   - Props: `{document: Document, onClick: (id) => void}`

2. **MarkdownRenderer** - Renders markdown with syntax highlighting, Mermaid diagrams, copy buttons
   - Dependencies: react-markdown, Mermaid.js, Prism.js, DOMPurify
   - Props: `{content: string, enableMermaid: boolean, enableTOC: boolean}`

3. **TableOfContents** - Auto-generated TOC from markdown headings with smooth scroll
   - Dependencies: React hooks, Intersection Observer
   - Props: `{content: string, enableActiveTracking: boolean}`

4. **EpicStoryTable** - Hierarchical table of epic-story relationships with expandable rows
   - Dependencies: shadcn/ui Table, StatusBadge
   - Props: `{graphData: GraphData, onNodeClick: (id) => void}`

5. **StatusBadge** - Color-coded status indicator (draft=gray, dev=blue, done=green)
   - Dependencies: shadcn/ui Badge
   - Props: `{status: 'draft' | 'dev' | 'done', size: 'sm' | 'md'}`

6. **SyncStatusIndicator** - Header widget with last sync timestamp and "Sync Now" button
   - Dependencies: React Query polling, shadcn/ui Toast
   - Props: `{project: Project, onSyncTrigger: () => void}`

### Backend Services

**Core Services:**

1. **GitHubSyncService** - Fetches markdown files from GitHub, stores in DB, triggers extraction
   - Methods: `sync_repository()`, `fetch_repository_tree()`
   - Dependencies: PyGithub, ProjectRepository, DocumentRepository

2. **LLMExtractionService** - OLLAMA-based extraction of structured data (epics, stories, status)
   - Methods: `extract_epic()`, `extract_story()`, `extract_status()`
   - Dependencies: OLLAMA client, Pydantic AI, Repositories

3. **RelationshipBuilderService** - Parses markdown links to build epic→story relationships
   - Methods: `build_relationships()`, `resolve_link()`
   - Dependencies: DocumentRepository, RelationshipRepository

4. **CacheService** - Redis-based caching for API responses (5-min TTL)
   - Methods: `get()`, `set()`, `invalidate_pattern()`
   - Dependencies: redis-py

### Component Interaction Diagram

```mermaid
graph TB
    User --> Router[React Router]
    Router --> Pages[Page Components]
    Pages --> DocumentCard
    Pages --> MarkdownRenderer
    Pages --> EpicStoryTable
    Pages --> SyncStatus[SyncStatusIndicator]
    Pages --> APIClient[API Client]

    APIClient --> FastAPI[FastAPI Routes]
    FastAPI --> GitHubSync[GitHubSyncService]
    FastAPI --> Extraction[LLMExtractionService]
    FastAPI --> RelBuilder[RelationshipBuilderService]
    FastAPI --> Cache[CacheService]
    FastAPI --> Repos[Repositories]

    GitHubSync --> GitHub[GitHub API]
    Extraction --> OLLAMA
    Repos --> PostgreSQL
    Cache --> Redis
```

---

## External APIs

### GitHub REST API v3

- **Purpose:** Fetch markdown files from public GitHub repositories
- **Documentation:** https://docs.github.com/en/rest
- **Base URL:** `https://api.github.com`
- **Authentication:** GitHub Personal Access Token (optional for POC, recommended)
- **Rate Limits:** 60 req/hr (unauthenticated), 5000 req/hr (authenticated)

**Key Endpoints:**
- `GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1` - Get repository tree
- `GET /repos/{owner}/{repo}/contents/{path}` - Get file contents

**Integration Notes:**
- Use PyGithub library for Python client
- Implement exponential backoff for rate limit errors
- Filter for `/docs` folder only

### OLLAMA API (External Server)

- **Purpose:** LLM inference for extracting structured BMAD content
- **Documentation:** https://github.com/jmorganca/ollama/blob/main/docs/api.md
- **Base URL:** Configured via environment variable `OLLAMA_BASE_URL` (e.g., `http://your-ollama-server:11434`)
- **Authentication:** None (configure if your server requires it)
- **Rate Limits:** N/A (managed by your OLLAMA server)

**Key Endpoints:**
- `POST /api/generate` - Generate text completion
- `GET /api/tags` - List available models

**Integration Notes:**
- Use `ollama-python` library configured to point to external server
- 30-second timeout per document (configurable via `OLLAMA_TIMEOUT`)
- Your existing GPU-enabled OLLAMA server will be used
- Model selection (Llama 3 8B or Mistral 7B) from Story 1.7 benchmarking
- Backend connects to external OLLAMA server via HTTP API
- Network connectivity required between backend and OLLAMA server

---

## Core Workflows

### Workflow 1: First-Time Project Setup and Sync

```mermaid
sequenceDiagram
    User->>Frontend: Enter GitHub URL
    Frontend->>API: POST /projects
    API->>DB: INSERT project
    API-->>Frontend: 201 Created

    User->>Frontend: Click "Sync Now"
    Frontend->>API: POST /projects/{id}/sync
    API-->>Frontend: 202 Accepted

    API->>GitHub: GET repository tree
    GitHub-->>API: File list

    loop For each .md file
        API->>GitHub: GET file content
        API->>DB: INSERT document
    end

    loop For each epic/story
        API->>OLLAMA: Extract structured data
        OLLAMA-->>API: JSON response
        API->>DB: INSERT extracted data
    end

    API->>DB: Build relationships
    API->>Redis: Invalidate cache

    Frontend->>API: GET /sync-status (polling)
    API-->>Frontend: {status: "completed"}
    Frontend->>API: GET /documents
    API-->>Frontend: Documents array
    Frontend->>User: Display dashboard
```

### Workflow 2: Navigating from Epics View to Document Detail

```mermaid
sequenceDiagram
    User->>Frontend: Navigate to /epics
    Frontend->>API: GET /relationships
    API->>Redis: Check cache
    Redis-->>API: HIT
    API-->>Frontend: GraphData
    Frontend->>User: Render table

    User->>Frontend: Click epic row
    Frontend->>API: GET /documents/{id}
    API->>DB: Query document + extracted_epic
    DB-->>API: Data
    API-->>Frontend: Document
    Frontend->>User: Render markdown + TOC
```

---

## Database Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    github_url TEXT NOT NULL,
    last_sync_timestamp TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(50) NOT NULL DEFAULT 'idle',
    sync_progress JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    doc_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    excerpt TEXT,
    last_modified TIMESTAMP WITH TIME ZONE,
    embedding vector(384),
    extraction_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    extraction_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_project_file UNIQUE(project_id, file_path)
);

CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE INDEX idx_documents_doc_type ON documents(doc_type);
CREATE INDEX idx_documents_extraction_status ON documents(extraction_status);

CREATE TABLE extracted_epics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
    epic_number INTEGER,
    title VARCHAR(500) NOT NULL,
    goal TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    story_count INTEGER DEFAULT 0,
    confidence_score FLOAT,
    extracted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_extracted_epics_document_id ON extracted_epics(document_id);

CREATE TABLE extracted_stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
    story_number VARCHAR(50) NOT NULL,
    role VARCHAR(255),
    action TEXT,
    benefit TEXT,
    acceptance_criteria JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    confidence_score FLOAT,
    extracted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_extracted_stories_document_id ON extracted_stories(document_id);

CREATE TABLE relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    child_doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_parent_child UNIQUE(parent_doc_id, child_doc_id, relationship_type),
    CONSTRAINT no_self_reference CHECK (parent_doc_id != child_doc_id)
);

CREATE INDEX idx_relationships_parent ON relationships(parent_doc_id);
CREATE INDEX idx_relationships_child ON relationships(child_doc_id);

CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    better_than_github BOOLEAN NOT NULL,
    favorite_feature VARCHAR(255),
    improvement_suggestions TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---

## Frontend Architecture

### Component Organization

```
apps/web/src/
├── components/
│   ├── ui/            # shadcn/ui base components
│   ├── layout/        # Header, TabNavigation, Breadcrumbs, Sidebar
│   ├── cards/         # DocumentCard, StatusCard, EpicCard
│   ├── markdown/      # MarkdownRenderer, TableOfContents, CodeBlock, MermaidDiagram
│   ├── epics/         # EpicStoryTable, EpicStoryGraph, StatusRollupWidget
│   └── sync/          # SyncStatusIndicator, SyncProgressToast, ProjectSetupModal
├── pages/             # LandingPage, ScopingView, ArchitectureView, EpicsView, DetailView
├── services/          # apiClient, projectsService, documentsService, epicsService
├── hooks/             # useProjects, useDocuments, useSyncStatus, useToast
├── stores/            # ThemeContext, ProjectContext
├── utils/             # formatDate, parseMarkdown, validation
├── styles/            # globals.css, theme.css
├── App.tsx
└── main.tsx
```

### Routing Structure

```typescript
/ → Landing/Project Setup
/scoping → Scoping View
/architecture → Architecture View
/epics → Epics View
/detail/:documentId → Detail View
```

### State Management

- **Server State:** React Query (5-min stale time, automatic refetch on window focus)
- **UI State:** React Context (current project, theme)
- **Local State:** useState for component-specific state
- **Form State:** Controlled components with useState

### API Client Setup

```typescript
// Axios instance with interceptors
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Response interceptor for global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log to Sentry, show toast notification
    return Promise.reject(error);
  }
);
```

---

## Backend Architecture

### Service Organization

```
apps/api/src/
├── routes/            # FastAPI route modules
├── services/          # Business logic (GitHubSyncService, LLMExtractionService, etc.)
├── repositories/      # Data access layer (BaseRepository, ProjectRepository, etc.)
├── models/            # SQLAlchemy ORM models
├── schemas/           # Pydantic request/response schemas
├── middleware/        # error_handler, request_logging, cors
├── core/              # config, database, redis, ollama
├── utils/             # Utilities
└── main.py            # FastAPI app entry
```

### Repository Pattern

```python
class BaseRepository(Generic[ModelType]):
    async def get_by_id(self, id: UUID) -> Optional[ModelType]: ...
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]: ...
    async def create(self, **kwargs) -> ModelType: ...
    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]: ...
    async def delete(self, id: UUID) -> bool: ...
```

### Authentication (Phase 2)

- **Method:** GitHub OAuth + JWT tokens
- **Token Storage:** httpOnly cookies
- **Session Management:** 30-min access token, 7-day refresh token
- **Middleware:** `get_current_user()` dependency for protected routes

---

## Unified Project Structure

```
bmadflow/
├── .github/workflows/         # CI/CD (ci.yaml, lint.yaml, deploy.yaml)
├── apps/
│   ├── web/                   # React SPA
│   │   ├── src/               # Components, pages, hooks, services
│   │   ├── public/
│   │   ├── tests/
│   │   └── package.json
│   └── api/                   # FastAPI backend
│       ├── src/               # Routes, services, repositories, models
│       ├── tests/
│       ├── alembic/           # Database migrations
│       └── requirements.txt
├── packages/
│   ├── shared/                # Shared TypeScript types
│   └── config/                # Shared ESLint, TypeScript configs
├── infrastructure/
│   ├── docker-compose.yml
│   └── nginx.conf
├── scripts/                   # setup.sh, dev.sh, test.sh
├── docs/                      # prd.md, front-end-spec.md, architecture.md
├── .env.example
├── package.json               # npm workspaces
└── README.md
```

---

## Development Workflow

### Prerequisites

```bash
node --version  # 20.x+
python --version  # 3.11+
docker --version  # 24.0+
```

### Initial Setup

```bash
git clone https://github.com/your-org/bmadflow.git
cd bmadflow
cp .env.example .env

npm install  # Install all workspace packages

cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Note: OLLAMA runs on external server, configure OLLAMA_BASE_URL in .env
# Verify OLLAMA server has required model (llama3:8b or mistral:7b)

cd ../..
docker compose up -d
```

### Development Commands

```bash
# Start all services
docker compose up

# Frontend only (hot reload)
npm run dev --workspace=apps/web

# Backend only (hot reload)
cd apps/api && uvicorn src.main:app --reload

# Run tests
npm run test  # Frontend
cd apps/api && pytest  # Backend

# Lint/format
npm run lint
cd apps/api && black src/ && ruff check src/

# Database migrations
cd apps/api && alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Environment Variables

```bash
# Frontend (.env.local)
VITE_API_BASE_URL=http://localhost:8000/api

# Backend (.env)
DATABASE_URL=postgresql+asyncpg://bmadflow:password@localhost:5432/bmadflow
REDIS_URL=redis://localhost:6379/0
OLLAMA_BASE_URL=http://your-ollama-server:11434  # Point to your existing OLLAMA server
OLLAMA_MODEL=llama3:8b  # Model available on your OLLAMA server
OLLAMA_TIMEOUT=30  # Timeout in seconds
GITHUB_TOKEN=  # Optional
SECRET_KEY=change-in-production
```

---

## Deployment Architecture

### Deployment Strategy

**Frontend:**
- Docker container with Nginx serving static build (`npm run build`)
- Build output: `apps/web/dist/`
- Phase 2: CDN (Cloudflare)

**Backend:**
- Docker container with uvicorn + FastAPI
- Phase 2: Kubernetes with Helm charts

**Database:**
- PostgreSQL Docker container (POC)
- Phase 2: Managed PostgreSQL (AWS RDS, GCP Cloud SQL)

**OLLAMA:**
- External server (existing GPU-enabled infrastructure)
- FastAPI backend connects via HTTP API
- No deployment needed (uses existing server)

### CI/CD Pipeline

GitHub Actions workflow:
1. **Frontend Tests:** ESLint, Vitest, build check
2. **Backend Tests:** Black, Ruff, pytest with coverage
3. **Accessibility Audit:** Lighthouse CI (score ≥90)
4. **Deploy:** (Phase 2) Deploy to production on main branch merge

### Environments

| Environment | Frontend | Backend | Purpose |
|-------------|----------|---------|---------|
| Development | localhost:5173 | localhost:8000 | Local dev |
| Production | bmadflow.internal | api.bmadflow.internal | Live |

---

## Security and Performance

### Security Requirements

**Frontend:**
- CSP headers to prevent XSS
- DOMPurify sanitizes markdown HTML
- No sensitive data in localStorage (POC)

**Backend:**
- Pydantic validation for all inputs
- SQLAlchemy parameterized queries (SQL injection prevention)
- Nginx rate limiting: 10 req/sec per IP
- CORS: Explicit origin whitelist only

**Phase 2 Auth:**
- JWT tokens in httpOnly cookies
- 30-min access token expiry
- GitHub OAuth only

### Performance Optimization

**Frontend:**
- Bundle size: <300KB gzipped
- Route-based code splitting (React.lazy)
- React Query 5-min cache
- Image lazy loading

**Backend:**
- Response time: <500ms (documents list), <200ms (single document)
- Database indexes on frequently queried columns
- Redis caching: 5-min TTL, >80% hit rate target
- Connection pooling: 5 baseline, 10 max

---

## Testing Strategy

### Testing Pyramid

```
       E2E (Manual POC)
      /                \
     Integration Tests
    /                    \
   Frontend Unit (30%)  Backend Unit (50%)
```

**POC Targets:**
- Frontend: 30% coverage (critical components)
- Backend: 50% coverage (services, repositories, routes)
- E2E: Manual testing with pilot users

**Phase 2 Targets:**
- Frontend: 70%, Backend: 80%, E2E: Playwright automation

### Test Organization

**Frontend:** `apps/web/tests/` - Vitest + React Testing Library

**Backend:** `apps/api/tests/` - pytest + pytest-asyncio + httpx

### Example Tests

**Frontend Component Test:**
```typescript
describe('MarkdownRenderer', () => {
  it('renders markdown headings', () => {
    render(<MarkdownRenderer content="# Hello" />);
    expect(screen.getByRole('heading')).toHaveTextContent('Hello');
  });
});
```

**Backend API Test:**
```python
@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    response = await client.post("/api/projects", json={"github_url": "https://github.com/owner/repo"})
    assert response.status_code == 201
    assert response.json()["name"] == "repo"
```

---

## Coding Standards

### Critical Rules

- **Type Sharing:** Define types in `packages/shared/`, import as `@bmadflow/shared/types`
- **API Calls:** Use service layer + React Query hooks, never direct `fetch()`
- **Environment Variables:** Access via config objects only
- **Error Handling:** Use standard ApiError format
- **State Updates:** Never mutate state directly
- **Database Queries:** Always use repository pattern
- **Async/Await:** Use `async/await`, never `.then()` chains

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| React Components | PascalCase | `DocumentCard.tsx` |
| Hooks | camelCase + 'use' | `useProjects.ts` |
| API Routes | kebab-case | `/api/sync-status` |
| Python Functions | snake_case | `sync_repository()` |
| Database Tables | snake_case plural | `extracted_epics` |
| Constants | SCREAMING_SNAKE_CASE | `API_TIMEOUT` |

---

## Error Handling Strategy

### Error Response Format

```typescript
interface ApiError {
  error: {
    code: string;           // "PROJECT_NOT_FOUND"
    message: string;        // Human-readable
    details?: object;       // Additional context
    timestamp: string;      // ISO 8601
    requestId: string;      // UUID for tracing
  };
}
```

### Frontend Error Handling

- Axios interceptor catches all API errors
- Log to Sentry with context
- Display user-friendly toast notifications
- React Query error state management
- Auto-retry with exponential backoff for network errors

### Backend Error Handling

- Global exception handler in FastAPI middleware
- Consistent ApiError format for all errors
- Request ID for tracing in logs
- Structured logging (JSON to stdout)

---

## Monitoring and Observability

### Monitoring Stack

- **Frontend:** Browser console errors, Sentry
- **Backend:** Prometheus + Grafana (Phase 2), Sentry
- **Error Tracking:** Sentry for both frontend and backend
- **Logging:** Python structured logging to stdout (Docker logs)

### Key Metrics

**Frontend:**
- Core Web Vitals (LCP, FID, CLS)
- JavaScript errors
- API response times

**Backend:**
- Request rate, error rate, response time
- Database query performance
- LLM extraction latency

---

## Architecture Checklist

**Ready for Development:** ✅

**Checklist Summary:**
- ✅ Platform and infrastructure defined (Docker Compose, self-hosted)
- ✅ Technology stack finalized (React, FastAPI, PostgreSQL, OLLAMA)
- ✅ Data models designed with TypeScript interfaces
- ✅ API specification documented (REST, OpenAPI)
- ✅ Component architecture defined (frontend + backend)
- ✅ Database schema provided with migrations
- ✅ Project structure defined (monorepo, npm workspaces)
- ✅ Development workflow documented
- ✅ Deployment strategy outlined
- ✅ Security and performance requirements specified
- ✅ Testing strategy defined
- ✅ Coding standards established
- ✅ Error handling strategy documented
- ✅ Monitoring approach defined

**Epic and Story Files:**
- Epic files: `docs/epics/` (4 epic files: [epic-1-foundation-github-dashboard.md](../epics/epic-1-foundation-github-dashboard.md) through [epic-4-epic-story-visualization.md](../epics/epic-4-epic-story-visualization.md))
- Story files: `docs/stories/` (33 story files: [story-1-1-project-infrastructure-setup.md](../stories/story-1-1-project-infrastructure-setup.md) through story-4-7)
- Each story references this architecture document for technical implementation guidance

**Next Steps:**
1. Developer executes [Story 1.1: Project Infrastructure Setup](../stories/story-1-1-project-infrastructure-setup.md)
2. Implement database schema ([Story 1.2](../stories/story-1-2-database-schema-for-documents.md))
3. Begin [Epic 1](../epics/epic-1-foundation-github-dashboard.md) development following this architecture

---

**Document Status:** ✅ **Complete and Ready for Development**

**Owner:** Winston (Architect)

**Next Review:** After POC Week 2 (architecture validation checkpoint)
