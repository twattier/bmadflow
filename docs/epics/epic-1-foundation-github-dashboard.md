# Epic 1: Foundation, GitHub Integration & Dashboard Shell

**Status:** Draft

## Epic Goal

Establish core infrastructure (Docker, Postgres, FastAPI, React + Vite + shadcn/ui) and deliver working dashboard shell with 4-view tab navigation. Backend can fetch and store raw GitHub markdown files. First deployable increment shows UI architecture and "look and feel."

## Epic Description

This epic establishes the foundational infrastructure for BMADFlow, setting up the complete development environment and delivering the first visible increment: a working dashboard shell with 4-view navigation. By the end of this epic, developers can run the entire application locally with Docker Compose, the backend can sync GitHub repositories and store markdown files in PostgreSQL, and users can see the basic UI structure (Scoping, Architecture, Epics, Detail views).

The epic includes critical infrastructure decisions like LLM provider selection (Story 1.7 - choosing between OLLAMA local or LiteLLM proxy based on privacy, capability, and embedding compatibility) and CI/CD pipeline setup (Story 1.8), ensuring the foundation supports the 4-6 week POC timeline.

## Stories

### Story 1.1: Project Infrastructure Setup

As a **developer**,
I want **Docker Compose configuration with all required services**,
so that **I can run the entire application locally with a single command**.

**Acceptance Criteria:**

1. Docker Compose file defines services: frontend (Vite dev server), backend (FastAPI), postgres (with pgvector extension)
2. Running `docker-compose up` starts all services successfully
3. Services can communicate (frontend can reach backend API, backend can connect to database)
4. Volume mounts configured for hot reload during development (code changes reflect without rebuild)
5. Environment variables documented in `.env.example` file
6. README includes "Getting Started" section with setup instructions (prerequisites, commands)
7. Health check endpoint `/api/health` returns 200 OK when backend is ready
8. Dependency conflict check: `npm install` completes without peer dependency warnings, `pip install` completes without version conflicts

### Story 1.2: Database Schema for Documents

As a **backend developer**,
I want **PostgreSQL schema to store projects, documents, and their metadata**,
so that **synced GitHub content can be persisted and queried**.

**Acceptance Criteria:**

1. Database migration creates `projects` table with fields: id (UUID), name, github_url, last_sync_timestamp, created_at
2. Database migration creates `documents` table with fields: id (UUID), project_id (FK), file_path, content (TEXT), doc_type (enum: scoping/architecture/epic/story/qa/other), last_modified, created_at
3. Database migration creates `relationships` table with fields: id (UUID), parent_doc_id (FK), child_doc_id (FK), relationship_type (enum: contains/relates_to), created_at
4. pgvector extension installed and `documents` table has `embedding` column (vector(384)) for future semantic search
5. Indexes created on commonly queried fields (project_id, file_path, doc_type)
6. Migration can be run with `alembic upgrade head` command

### Story 1.3: GitHub API Integration - Fetch Repository Files

As a **backend developer**,
I want **service to fetch markdown files from public GitHub repositories**,
so that **users can sync their documentation into BMADFlow**.

**Acceptance Criteria:**

1. GitHub service class accepts repository URL (format: `github.com/org/repo`) and validates format
2. Service requires GitHub Personal Access Token as parameter (stored in environment variables)
3. Service fetches repository tree from `/docs` folder using GitHub REST API v3
4. Service recursively retrieves all `.md` files and their content
5. Service handles GitHub API errors gracefully (404 not found, 403 rate limit, network errors) with descriptive error messages
6. Manual test confirms: can fetch all docs from `github.com/bmad-code-org/BMAD-METHOD` repo in <2 minutes

### Story 1.4: Manual Sync API Endpoint

As a **user**,
I want **API endpoint to trigger GitHub repository sync**,
so that **I can manually update BMADFlow with latest documentation changes**.

**Acceptance Criteria:**

1. POST `/api/projects` endpoint accepts JSON body with `github_url` and creates project record in database
2. POST `/api/projects/{project_id}/sync` endpoint triggers background sync task using FastAPI BackgroundTasks
3. Endpoint validates project exists and github_url is accessible before starting sync
4. Sync process: (1) Fetch files from GitHub, (2) Store raw markdown in documents table, (3) Update project last_sync_timestamp
5. Endpoint returns 202 Accepted with sync task ID immediately (doesn't block while syncing)
6. GET `/api/projects/{project_id}/sync-status` endpoint returns current sync progress (status: pending/in_progress/completed/failed, processed_count, total_count, error_message if failed)
7. Sync process stores each document with detected doc_type (infer from file path: `/docs/prd/` = scoping, `/docs/architecture/` = architecture, `/docs/epics/` = epic, `/docs/stories/` = story, `/docs/qa/` = qa, other paths = other)
8. If sync fails, sync-status endpoint includes error_message and retry_allowed flag
9. Integration test confirms: full sync of 50-doc repository completes in <5 minutes, all documents stored correctly

### Story 1.5: Dashboard Shell with 4-View Navigation

As a **user**,
I want **dashboard with tab navigation between 4 views**,
so that **I can explore different aspects of my project documentation**.

**Acceptance Criteria:**

1. React application created with Vite + TypeScript + Tailwind CSS
2. shadcn/ui components installed and configured (button, card, tabs, navigation)
3. Top navigation bar displays: BMADFlow logo, project name selector (hardcoded to single project for POC), sync status indicator
4. Tab navigation shows 4 tabs with icons and labels: 📋 Scoping, 🏗️ Architecture, 📊 Epics, 🔍 Detail
5. Clicking tab navigates to corresponding route using React Router (`/scoping`, `/architecture`, `/epics`, `/detail`)
6. Active tab visually highlighted (underline + bold text per UX spec)
7. Each view renders placeholder content initially (Scoping and Detail views implemented first, Architecture and Epics added in Epic 3)
8. Responsive design works on desktop (1920×1080 and 1440×900 tested)
9. Manual test confirms: navigation between implemented views works smoothly, no console errors

### Story 1.6: Project Setup and Sync UI

As a **user**,
I want **UI to add GitHub repository and trigger sync**,
so that **I can load my documentation into BMADFlow**.

**Acceptance Criteria:**

1. Landing page displays "Add Project" form with input field for GitHub URL and "Sync Now" button
2. Input validation shows error if URL format incorrect (must match `github.com/org/repo` pattern)
3. Clicking "Sync Now" calls POST `/api/projects` with github_url, then immediately calls POST `/api/projects/{id}/sync`
4. Form disabled during sync with loading spinner and "Syncing..." message
5. Sync progress shown via polling GET `/api/projects/{id}/sync-status` every 2 seconds
6. Progress display shows: "Syncing... X of Y documents processed"
7. On sync complete (status = completed), redirect to `/scoping` view
8. On sync failure (status = failed), display error message with "Retry" button that calls POST /sync endpoint again
9. After successful sync, project name appears in top navigation bar
10. Manual test confirms: adding `github.com/bmad-code-org/BMAD-METHOD` repo completes sync flow end-to-end

### Story 1.7: LLM Provider Selection and Validation

As a **developer**,
I want **to evaluate OLLAMA (local) and LiteLLM proxy (remote) LLM provider options for BMAD document extraction**,
so that **Epic 2 can use the selected provider with appropriate configuration**.

**Acceptance Criteria:**

1. Evaluation script tests 2 LLM provider options: OLLAMA local (qwen2.5:3b with nomic-embed-text) and OpenAI-compatible API via custom LiteLLM proxy (configurable endpoint + API key)
2. Test dataset: 20 BMAD sample documents (10 epics + 10 stories from BMAD-METHOD repo) for extraction validation
3. Measure for each provider: (1) Extraction accuracy (manual validation), (2) Latency per document, (3) Cost per document, (4) Embedding dimension compatibility
4. Document critical finding: Embedding dimension mismatch issue (nomic-embed: 768d vs proxy dimension) prevents provider switching after initial data load
5. Results documented in docs/llm-provider-evaluation.md with recommendation based on: privacy (weight: 40%), extraction capability (30%), cost (20%), latency (10%)
6. Selected provider configured for Epic 2 with environment variables and architecture documentation updated

### Story 1.8: CI/CD Pipeline Setup

As a **developer**,
I want **GitHub Actions CI/CD pipeline for automated testing and quality checks**,
so that **code quality issues are caught early and deployment is automated**.

**Acceptance Criteria:**

1. GitHub Actions workflow file `.github/workflows/ci.yml` created with jobs for frontend and backend
2. Frontend job runs: ESLint checks, TypeScript compilation, Vitest unit tests, build verification
3. Backend job runs: Black formatting check, Ruff linting, pytest with coverage report (target 50%+)
4. Workflow triggers on pull requests and pushes to main branch
5. Workflow completes in under 5 minutes for typical changes
6. Test failures prevent PR merge (required status checks configured)
7. Badge added to README showing build status
8. Optional: Lighthouse CI job for accessibility audit (target score ≥90) runs on frontend changes

## Dependencies

- External OLLAMA server must be available and accessible
- GitHub Personal Access Token recommended (avoids rate limits)
- Docker 24.0+, Node 20+, Python 3.11+ required

## Success Metrics

- All 8 stories completed with acceptance criteria met
- Full local development environment working with single `docker-compose up` command
- GitHub sync functional on 50+ document repository
- Dashboard shell navigable across all 4 views
- CI/CD pipeline operational and passing

## Timeline

**Target:** Week 1 of POC (5 working days)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Epic extracted from PRD v1.0 | Sarah (PO) |
| 2025-10-02 | 1.1 | Updated Story 1.7: Changed from "OLLAMA Model Benchmarking" (3 models, 50 docs) to "LLM Provider Selection" (2 providers: OLLAMA vs LiteLLM proxy, 20 docs, embedding dimension analysis). Reflects actual requirement: select one provider for application, not compare multiple models. | Sarah (PO) |
