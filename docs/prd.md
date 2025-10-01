# BMADFlow Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Validate product-market fit with 80% of POC users rating BMADFlow as "significantly better" than GitHub navigation
- Achieve 90%+ LLM extraction accuracy for BMAD-structured documents (epics, stories, status)
- Reduce documentation navigation time by 80% (from 15 min to 3 min)
- Enable new team member onboarding in 1 day instead of 2-3 days
- Reduce stakeholder meeting prep time by 90% (from 30-60 min to 5 min)
- Deliver POC within 4-6 weeks with 1 developer + Claude Code
- Establish foundation for $2.5-3M ARR by Year 3

### Background Context

BMADFlow addresses a critical pain point faced by 78% of development teams: poor documentation navigation wastes 15+ minutes per search and creates barriers to project understanding. Software teams using structured methodologies (BMAD, SAFe, Scrum@Scale) create extensive documentation stored as markdown in GitHub, but GitHub's file-by-file navigation is painfully slow and provides no project visibility.

BMADFlow is an intelligent documentation visualization platform that transforms scattered GitHub markdown files into interactive, methodology-aware project dashboards. By combining AI-powered content extraction (using OLLAMA for privacy), epic-to-story graph visualization, and purpose-built multi-view dashboards, BMADFlow enables teams to find information 80% faster while providing stakeholders with instant project status visibility - all without migrating away from GitHub as the single source of truth.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Initial PRD created from project brief | John (PM) |
| 2025-10-01 | 1.1 | Extracted 4 epics and 33 stories to individual files | Sarah (PO) |

---

## Requirements

### Functional Requirements

**FR1:** The system shall accept GitHub repository URLs and validate format before processing

**FR2:** The system shall fetch documentation from GitHub `/docs` folders via GitHub API with manual sync trigger

**FR3:** The system shall extract structured information from markdown files using OLLAMA LLM including: (1) User story components ("As a/I want/So that"), (2) Acceptance criteria lists, (3) Status values (draft/dev/done), (4) Epic titles and descriptions, (5) Story-to-epic relationships via markdown links or content analysis

**FR4:** The system shall achieve 90%+ extraction accuracy on BMAD-structured documents, measured by manual validation of 100 sample extractions against ground truth labels for user stories, epics, and status fields

**FR5:** The system shall provide a multi-view dashboard with four distinct views: Scoping (📋), Architecture (🏗️), Epics (📊), and Detail (🔍)

**FR6:** The system shall display document cards in Scoping view showing research docs, PRD sections, and use case specs with titles, summaries, and status badges

**FR7:** The system shall render architecture documentation with Mermaid diagrams, tech stack details, and system design docs

**FR8:** The system shall visualize epic-to-story relationships as an interactive graph with zoom/pan controls and status color-coding (draft=gray, dev=blue, done=green), with table view as fallback if graph rendering fails

**FR9:** The system shall provide detailed document view with full markdown rendering, auto-generated table of contents, and clickable inter-document links

**FR10:** The system shall render Mermaid.js diagrams, syntax-highlighted code blocks, and maintain responsive design for desktop and tablet (mobile as stretch goal)

**FR11:** The system shall complete sync operations in under 5 minutes for typical projects (50-100 documents)

**FR12:** The system shall support only public GitHub repositories for POC (authentication optional for avoiding rate limits)

**FR13:** The system shall persist project metadata, documents, extracted content, and relationship graphs using appropriate storage solutions (specific technologies determined by Architecture)

**FR14:** The system shall display sync status indicators (in progress, completed, errors) with progress feedback during operations

**FR15:** The system shall enable navigation between documents via clickable inter-document links that resolve to correct dashboard views

**FR16:** The system shall display actionable error messages with retry options when sync fails, extraction errors occur, or documents cannot be processed

**FR17:** The system shall gracefully handle GitHub API rate limits by providing clear feedback and implementing request throttling or requiring authentication for higher limits

**FR18:** The system shall provide keyword search across document titles and content with results displayed in under 500ms (POC: client-side title filtering; Phase 2: server-side full-text search with context snippets)

**FR19:** The system shall identify and report documents with missing or malformed BMAD structure (e.g., stories without acceptance criteria, invalid status values)

**FR20:** The system shall provide a feedback mechanism for pilot users to rate UX improvement (1-5 stars) and feature value, supporting POC success measurement

### Non-Functional Requirements

**NFR1:** The system shall load the dashboard in under 3 seconds on broadband connections

**NFR2:** The system shall render 10,000-word documents in under 2 seconds

**NFR3:** The system shall handle 20-50 graph nodes without performance degradation (target 60fps animations)

**NFR4:** The system shall use self-hosted OLLAMA running on project infrastructure (not cloud AI services) for LLM inference to ensure documentation privacy and avoid external API costs

**NFR5:** The system shall maintain WCAG 2.1 Level AA accessibility compliance as specified in UX requirements (color contrast, keyboard navigation, screen reader support)

**NFR6:** The system shall support Chrome 90+, Firefox 88+, Safari 14+, and Edge 90+ browsers

**NFR7:** The system shall be optimized for 3 concurrent pilot users during POC with single-user performance testing (multi-user load testing deferred to industrialization)

**NFR8:** The system shall use Docker containers for deployment consistency across development and production environments

**NFR9:** The system shall implement read-only access to GitHub repositories (no write operations, no data modification)

**NFR10:** The system shall complete POC development within 4-6 week timeline with 1 developer + Claude Code assistance, accepting that some features may be simplified or deferred

**NFR11:** The system shall provide Docker Compose configuration for local development with sample BMAD project data pre-loaded for rapid onboarding and testing

---

## User Interface Design Goals

### Overall UX Vision

BMADFlow provides a **significantly superior documentation exploration experience** compared to GitHub's file navigation, targeting 80% time reduction for finding information. The interface prioritizes **clarity over cleverness** with progressive disclosure - users see high-level project views first (dashboard cards, graph overviews), then drill down into details only when needed. The design aesthetic is **modern, professional, and trustworthy** to appeal to enterprise product teams, emphasizing efficiency and methodology expertise through intelligent organization rather than visual innovation.

### Key Interaction Paradigms

**Primary Navigation:** Top-level tab navigation for 4 core views (📋 Scoping, 🏗️ Architecture, 📊 Epics, 🔍 Detail) with icons and labels, always visible and accessible. Users switch contexts via single clicks between project phases.

**Progressive Disclosure:** Dashboard presents document cards and graph overviews first. Clicking reveals full content with table of contents navigation. Metadata panels (status, related docs, last modified) appear contextually in sidebars rather than cluttering main views.

**Graph Interaction:** Epic-to-story relationships visualized as interactive graph OR table/list view (POC may ship table first with graph as stretch goal if Week 5-6 timeline permits). Graph features include zoom/pan/center controls, click-to-navigate to detail views, and color-coded status at a glance.

**Instant Feedback:** Every action provides immediate visual response - sync shows progress bars, searches display results, errors show actionable guidance, clicks provide visual acknowledgment. No user action leaves them wondering "did that work?"

**Search-First Discovery:** Document filtering accessible from dashboard views. POC starts with simple title/keyword filtering; full semantic search (Cmd+K, instant results <500ms) deferred to industrialization.

### Core Screens and Views

1. **Landing/Project Setup Screen** - Add GitHub repo URL, validate, trigger sync **(POC Must-Have)**
2. **Dashboard - Scoping View (📋)** - Grid of document cards for research, PRD sections, use case specs **(POC Must-Have)**
3. **Dashboard - Architecture View (🏗️)** - Tech stack table, Mermaid architecture diagrams, system design sections **(POC Must-Have)**
4. **Dashboard - Epics View (📊)** - Table/list OR interactive graph of epic→story relationships with status rollup **(POC Must-Have)**
5. **Dashboard - Detail View (🔍)** - Full markdown rendering with TOC sidebar, metadata panel, related documents **(POC Must-Have)**
6. **Search/Filter Interface** - Simple document filtering by title/content **(POC Nice-to-Have)**
7. **Error/Status Screens** - Sync progress, error messages with retry options, empty states **(POC Must-Have)**

### Accessibility: WCAG 2.1 Level AA (Target)

**POC Approach:** Use shadcn/ui accessible components (built on Radix UI primitives) which provide WCAG AA compliance out-of-box. Automated testing only during POC; full manual validation deferred to industrialization.

- **Color contrast ratios:** Tailwind default palette meets 4.5:1 for text, 3:1 for UI components
- **Keyboard navigation:** All functionality accessible via Tab, Enter, Esc with visible focus indicators (shadcn/ui default)
- **Screen reader support:** Semantic HTML5, ARIA labels via Radix UI components
- **Touch targets:** Minimum 44×44px clickable areas
- **Automated testing:** axe-core integration, Lighthouse CI audits (target score ≥90)
- **Manual testing:** Deferred to industrialization (keyboard-only navigation, screen reader compatibility, zoom testing)

### Branding

**Visual Identity:** Modern, professional B2B SaaS aesthetic. Brand positioning: *"Intelligent documentation visualization for structured development teams"* - emphasizes clarity, efficiency, and methodology expertise.

**Design System:** shadcn/ui component library (accessible, customizable React components on Radix UI + Tailwind CSS). Primary color #3B82F6 (blue) for trust/professionalism, status colors follow universal conventions (green=done, amber=in-progress, red=blocked/draft).

**Typography:** Inter font family (sans-serif), JetBrains Mono for code. Type scale 1.25x ratio with line height 1.5 for body text.

**Iconography:** Lucide Icons (open-source, 2px stroke) at 20px inline, 24px for primary navigation.

### Target Device and Platforms: Web Responsive (Desktop Primary)

**Breakpoints:**
- **Desktop (1024px+):** Full layouts, optimal experience **(POC Primary Target)**
- **Tablet (768-1023px):** Adapted layouts **(POC Nice-to-Have)**
- **Mobile (320-767px):** Deferred to industrialization

**Platform Priorities for POC:**
1. **Desktop (1920×1080, 1440×900)** - Primary target, pilot users are desktop-based
2. **Tablet (1024×768+)** - Stretch goal if time permits
3. **Mobile** - Explicitly out of scope for POC

### POC Implementation Priorities

The UI goals above represent the complete product vision as defined in the UX specification. For the 4-6 week POC, implementation will focus on validating core navigation value with functional simplicity:

**Must-Have (POC):**
- 4-view dashboard navigation (tabs working, views render content)
- Basic table/list view of epic-story relationships with status indicators
- Detail view with markdown rendering (Mermaid diagrams, code highlighting, TOC)
- Desktop-optimized responsive design (1440×900 and 1920×1080 primary targets)
- shadcn/ui components out-of-box (minimal customization)
- Keyboard navigation and semantic HTML (automated accessibility checks only)

**Nice-to-Have (POC Stretch Goals):**
- Interactive graph with zoom/pan (ship table first, add graph if Week 5 permits)
- Simple document title/keyword filtering
- Tablet responsive breakpoints (768px+)
- Polish animations and micro-interactions

**Deferred to Industrialization:**
- Mobile responsive design (320-767px breakpoints)
- Full WCAG AA manual compliance testing and user testing with assistive tech
- Advanced graph features (multiple layouts, filtering, dependency visualization)
- Semantic/AI-powered search with Cmd+K and instant results
- Extensive animation polish and branding customization
- Advanced error recovery and retry mechanisms

---

## Technical Assumptions

### Repository Structure: Monorepo

Use monorepo structure with workspace tooling (npm workspaces or Turborepo) to house frontend, backend, and shared packages in a single repository.

**Rationale:** Frontend and backend share TypeScript types, simplifies CI/CD for single-developer POC, easier code sharing.

### Service Architecture: Modular Monolith (Backend) + SPA (Frontend)

**Architecture Style:**
- **Backend:** Python FastAPI monolithic application with modular services (GitHub sync, LLM extraction, API endpoints)
- **Frontend:** React Single Page Application (SPA) deployed separately
- **Deployment:** Docker containers with Docker Compose (Kubernetes deferred to industrialization)

**Rationale:** Microservices add unnecessary complexity for POC; modular monolith provides boundaries without distributed system overhead.

### Testing Requirements: Pragmatic POC Approach

**Testing Pyramid for POC:**
- **Backend Unit Tests:** Critical extraction logic, API endpoints (pytest) - Target 50% coverage
- **Backend Integration Tests:** GitHub API integration, LLM extraction end-to-end
- **Frontend Unit Tests:** Smoke tests only (React Testing Library + Vitest) - Target 30% coverage
- **E2E Tests:** Manual testing with pilot users (automated E2E deferred)

**Highest Priority:** Manual validation of LLM extraction on 100 sample documents (accuracy measurement more important than coverage metrics for POC).

**Rationale:** POC timeline prioritizes feature delivery; pilot user validation substitutes for extensive automation; industrialization brings coverage to 80%+.

### Additional Technical Assumptions and Requests

**Frontend Stack:**
- **Framework:** React 18+ with TypeScript
- **Build Tool:** Vite (faster HMR than Next.js, simpler for SPA)
- **UI Library:** shadcn/ui components with Tailwind CSS
- **State Management:** React Query for server state + Context API for UI state
- **Routing:** React Router v6
- **Markdown:** react-markdown + remark/rehype plugins
- **Diagrams:** mermaid.js
- **Graph:** React Flow (stretch goal) OR HTML table (must-have)

**Backend Stack:**
- **Framework:** Python FastAPI with uvicorn
- **Language:** Python 3.11+
- **AI/LLM:** Pydantic AI + OLLAMA (Llama 3 8B or Mistral 7B)
- **Async Processing:** FastAPI BackgroundTasks + WebSocket for progress streaming (Celery deferred to industrialization)
- **API Style:** RESTful JSON APIs

**Data Storage:**
- **Primary Database:** PostgreSQL 15+ with pgvector extension (documents, metadata, relationships via adjacency list)
- **Cache:** Redis (API response caching only)
- **Graph Database:** Deferred to industrialization (PostgreSQL sufficient for POC scale of 20-50 nodes)
- **File Storage:** Local filesystem for POC

**Infrastructure:**
- **Containerization:** Docker with multi-stage builds, Docker Compose for local dev
- **CI/CD:** GitHub Actions
- **Hosting:** Self-hosted on project infrastructure (internal/on-prem)
- **Monitoring:** Prometheus + Grafana (lightweight), Sentry (error tracking)

**External APIs:**
- **GitHub REST API v3:** Repository contents and metadata
- **Authentication:** Require GitHub Personal Access Token (avoids 60 req/hr rate limit, enables 5000 req/hr)

**Development Environment:**
- **IDE:** Claude Code for AI-assisted development
- **Version Control:** Git with GitHub
- **Code Quality:** ESLint (TypeScript/React), Black (Python), pre-commit hooks
- **Package Management:** npm (frontend), pip + virtualenv (backend)

**Security & Privacy:**
- **LLM Privacy:** OLLAMA self-hosted (no external AI providers)
- **Authentication:** Not required for POC (public repos), JWT deferred to industrialization
- **HTTPS:** Required for production, self-signed acceptable for local dev
- **Input Validation:** Pydantic models for API validation

**Performance Constraints:**
- **Sync Time:** Target <5 min for 100 docs (may require parallel processing)
- **Dashboard Load:** Target <3 sec (lazy loading per view)
- **LLM Inference:** 2-5 sec per document (faster with GPU)
- **Concurrent Users:** Optimized for 3 pilot users

**Additional Architecture Decisions:**

- **OLLAMA Model Selection:** Week 1 task is model benchmarking - test Llama 3 8B, Mistral 7B, and one 13B model on 50 BMAD sample documents, measure accuracy (manual validation) and latency, select best trade-off

- **OLLAMA Infrastructure:** GPU-enabled server preferred for 5-min sync target; CPU-only acceptable for POC if sync extends to 10 minutes (still validates value prop)

- **Data Loading Strategy:** Lazy load per dashboard view - fetch documents only when user navigates to view (reduces initial page load)

- **Sync Resilience:** Implement resumable sync with progress checkpoints - if sync fails at doc 50/100, retry from doc 51 (store last processed document ID)

- **Mermaid Rendering Fallback:** If Mermaid fails to render, display raw code block with warning (graceful degradation)

---

## Epic List

### Epic 1: Foundation, GitHub Integration & Dashboard Shell (8 stories)
**Goal:** Establish core infrastructure (Docker, Postgres, FastAPI, React + Vite + shadcn/ui) and deliver working dashboard shell with 4-view tab navigation. Backend can fetch and store raw GitHub markdown files. First deployable increment shows UI architecture and "look and feel."

### Epic 2: LLM-Powered Content Extraction (9 stories)
**Goal:** Implement OLLAMA-based extraction of structured information from BMAD markdown (user stories, epics, status, relationships). Developer validates extraction logic on 20 sample documents in Week 2. PM/pilot users perform comprehensive 100-document accuracy validation in parallel with Epic 3 (async validation, results inform Epic 3 refinements).

### Epic 3: Multi-View Documentation Dashboard (8 stories)
**Goal:** Create 4-view dashboard (Scoping, Architecture, Epics, Detail) with beautiful markdown rendering, Mermaid diagrams, and navigation. Deliver core "better than GitHub" UX value proposition.

**Critical Path Milestones:**
- **End of Week 3 (Must-Have):** Scoping view with document cards, Detail view with basic markdown rendering
- **End of Week 4 (Should-Have):** Architecture view, Mermaid diagram support, TOC navigation
- **End of Week 4 (Nice-to-Have):** Advanced formatting, inter-document link resolution

### Epic 4: Epic-Story Relationship Visualization (8 stories)
**Goal:** Build table/list visualization of epic-to-story relationships with status color-coding and click-to-navigate, enabling users to understand project structure at a glance. Interactive graph with zoom/pan as stretch goal if Week 5 timeline permits (Week 6 = polish, pilot testing, bug fixes).

---

## Epic 1: Foundation, GitHub Integration & Dashboard Shell

**Epic Goal:** Establish core infrastructure (Docker, Postgres, FastAPI, React + Vite + shadcn/ui) and deliver working dashboard shell with 4-view tab navigation. Backend can fetch and store raw GitHub markdown files. First deployable increment shows UI architecture and "look and feel."

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

### Story 1.7: OLLAMA Model Benchmarking

As a **developer**,
I want **to benchmark 3 LLM models on BMAD document extraction**,
so that **Epic 2 can use the best-performing model**.

**Acceptance Criteria:**

1. Benchmark script tests 3 models: Llama 3 8B, Mistral 7B, one 13B model
2. Test dataset: 50 BMAD sample documents (epics + stories from AgentLab repo or BMAD-METHOD repo)
3. Measure for each model: (1) Extraction accuracy (manual validation on 20 samples), (2) Latency (avg time per document), (3) Resource usage (GPU/CPU/memory)
4. Results documented in docs/model-benchmark-results.md with recommendation
5. Selected model configured for Epic 2 Story 2.1

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

---

## Epic 2: LLM-Powered Content Extraction

**Epic Goal:** Implement OLLAMA-based extraction of structured information from BMAD markdown (user stories, epics, status, relationships). Developer validates extraction logic on 20 sample documents in Week 2. PM/pilot users perform comprehensive 100-document accuracy validation in parallel with Epic 3.

**Prerequisites:** Week 1 Story 1.7 completed - GPU availability confirmed and model selected based on benchmarking.

### Story 2.1: OLLAMA Integration and Model Setup

As a **backend developer**,
I want **OLLAMA configured with selected LLM model**,
so that **extraction pipeline can perform inference on markdown documents**.

**Acceptance Criteria:**

1. OLLAMA service added to Docker Compose configuration (using `ollama/ollama` Docker image)
2. Selected model (from Story 1.7 benchmarking) pulled and loaded in OLLAMA container on startup
3. Python client library (`ollama-python`) installed and configured to communicate with OLLAMA service
4. Extraction service class can send prompt + document text to OLLAMA and receive structured JSON response
5. Service implements retry logic with exponential backoff for transient OLLAMA failures
6. Service includes timeout handling (default 30 sec per document, configurable)
7. Health check endpoint verifies OLLAMA is responding and model is loaded
8. Unit test confirms: service can send test prompt and receive response from OLLAMA

### Story 2.2: User Story Extraction

As a **backend developer**,
I want **LLM to extract user story components from story markdown files**,
so that **structured story data can be displayed in the dashboard**.

**Acceptance Criteria:**

1. Extraction service accepts markdown content and document type (story) as input
2. Service generates prompt instructing LLM to extract: (1) "As a" role, (2) "I want" action, (3) "So that" benefit, (4) Acceptance criteria list, (5) Status (draft/dev/done)
3. Service uses Pydantic AI structured output to enforce JSON schema for extracted data
4. Extracted data stored in new `extracted_stories` table with fields: document_id (FK), role, action, benefit, acceptance_criteria (JSONB array), status, confidence_score
5. Service handles extraction failures gracefully (if LLM can't parse, store raw content with status = 'extraction_failed')
6. Developer manually validates extraction on 20 sample story documents from BMAD-METHOD repo

### Story 2.3: Epic Extraction

As a **backend developer**,
I want **LLM to extract epic metadata from epic markdown files**,
so that **epic information can be displayed and linked to stories**.

**Acceptance Criteria:**

1. Extraction service extracts from epic documents: (1) Epic title, (2) Epic goal/description, (3) Status (draft/dev/done), (4) List of related story filenames (from markdown links like `[Story 1.2](stories/story-1-2.md)`)
2. Extracted data stored in `extracted_epics` table with fields: document_id (FK), title, goal, status, related_stories (JSONB array of story identifiers), confidence_score
3. Service parses markdown links to identify story relationships and stores in `relationships` table (parent = epic document_id, child = story document_id resolved from filename, relationship_type = 'contains')
4. Link resolution handles both relative paths (`stories/story-1-2.md`) and absolute paths (`/docs/stories/story-1-2.md`)
5. Unresolved links (story file doesn't exist) logged as warnings but don't fail extraction
6. Developer validates on 10 sample epic documents

### Story 2.4: Status Detection

As a **backend developer**,
I want **LLM to detect document status indicators**,
so that **dashboard can display color-coded status (draft/dev/done)**.

**Acceptance Criteria:**

1. Extraction service detects status from explicit markers in markdown: `Status: Draft`, `Status: Dev`, `Status: Done` (case-insensitive, various formats supported)
2. If no explicit status, LLM infers status from content analysis (acceptance criteria complete = likely dev/done, TODOs present = likely draft)
3. Status enum standardized to: draft, dev, done (maps to colors: gray, blue, green per UX spec)
4. Status stored in extracted_stories and extracted_epics tables
5. Developer validates status detection on 20 documents with known status labels
6. Validation target: 90%+ accuracy on documents with explicit status markers, 70%+ on documents requiring inference

### Story 2.5: Extraction Pipeline Integration

As a **backend developer**,
I want **extraction automatically triggered after GitHub sync completes**,
so that **extracted data is available immediately without manual step**.

**Acceptance Criteria:**

1. Sync process (from Story 1.4) extended: after storing raw documents, trigger extraction for each document
2. Extraction runs for all documents with doc_type = epic or story (scoping/architecture documents extracted in Epic 3)
3. Extraction parallelized: process 4 documents concurrently to reduce total time
4. Sync status endpoint updated to show extraction progress (syncing/extracting/complete phases)
5. Failed extractions logged with document_id and error message, but don't fail entire sync
6. Extraction results summary included in sync completion: total documents, successfully extracted, extraction failures, average confidence score
7. Integration test confirms: syncing 50-doc repo triggers extraction for all epics/stories, completes in <10 minutes (including OLLAMA inference time)

### Story 2.6: Extraction Accuracy Validation Tool

As a **PM/QA**,
I want **tool to validate extraction accuracy against ground truth**,
so that **we can measure whether 90% accuracy target is achieved**.

**Acceptance Criteria:**

1. CLI tool `python scripts/validate_extraction.py` accepts: (1) Project ID, (2) CSV file with ground truth labels (document_id, expected_role, expected_action, expected_status, etc.)
2. Tool queries extracted_stories and extracted_epics tables for specified project
3. Tool compares extracted values against ground truth and calculates per-field accuracy (role accuracy, action accuracy, status accuracy, overall accuracy)
4. Tool outputs validation report: total documents, correctly extracted (all fields match), partially correct (some fields match), failed, accuracy percentage per field
5. PM uses tool to validate 100-document test set (ground truth labels created manually)
6. Validation results documented in `docs/extraction-validation-results.md` with accuracy breakdown
7. Success criteria: Overall accuracy ≥90% on 100-document test set (if <90%, Stories 2.7a-c address improvements)

### Story 2.7a: Prompt Engineering Improvements

As a **backend developer**,
I want **to refine extraction prompts based on validation failures**,
so that **extraction accuracy improves**.

**Acceptance Criteria:**

1. Analyze validation results from Story 2.6 to identify top 3 failure patterns
2. Enhance LLM prompts with 5 few-shot examples demonstrating correct extraction
3. Add output format constraints to reduce parsing errors
4. Re-run extraction on 20 failed samples from validation set
5. Validation improvement: achieve ≥80% accuracy on previously failed samples

### Story 2.7b: Status Detection Fallback Rules

As a **backend developer**,
I want **regex-based fallback for status detection**,
so that **status accuracy improves when LLM inference is uncertain**.

**Acceptance Criteria:**

1. Add regex patterns for common status markers: "Status: X", "[STATUS: X]", "<!-- status: X -->"
2. If LLM confidence score <0.7, use regex fallback
3. Re-run validation on status field
4. Status detection accuracy improves to ≥85%

### Story 2.7c: Acceptance Criteria Parsing

As a **backend developer**,
I want **numbered list parser for acceptance criteria**,
so that **AC extraction accuracy improves**.

**Acceptance Criteria:**

1. Add structured parser for common AC formats: "1. AC text", "- AC text", "AC1: text"
2. If LLM fails to extract ACs (empty result), use structured parser as fallback
3. Re-run validation on AC field
4. AC extraction accuracy improves to ≥85%

---

## Epic 3: Multi-View Documentation Dashboard

**Epic Goal:** Create 4-view dashboard (Scoping, Architecture, Epics, Detail) with beautiful markdown rendering, Mermaid diagrams, and navigation. Deliver core "better than GitHub" UX value proposition.

**Critical Path:** Scoping + Detail views working by end of Week 3; Architecture view and Mermaid complete in Week 4.

### Story 3.1: Scoping View - Document Cards Grid

As a **user**,
I want **Scoping view to display grid of scoping documents as cards**,
so that **I can quickly see all research, PRD, and use case documents**.

**Acceptance Criteria:**

1. Scoping view fetches documents where doc_type = 'scoping' from `/api/projects/{id}/documents?type=scoping` endpoint
2. Documents displayed as card grid (3 columns on desktop per UX spec)
3. Each card shows: document title (extracted from first H1 heading), excerpt (first 150 characters of content), last modified date, status badge if available
4. Cards are clickable - clicking navigates to Detail view with document_id parameter
5. Cards show visual loading state (skeleton placeholders) while data fetches
6. Empty state displayed if no scoping documents found: "No scoping documents found. Check repository structure."
7. Search/filter input at top of grid (filters document titles as user types - simple client-side filtering for POC)

### Story 3.2: Detail View - Markdown Rendering

As a **user**,
I want **Detail view to render markdown content beautifully**,
so that **reading documentation in BMADFlow is significantly better than GitHub**.

**Acceptance Criteria:**

1. Detail view fetches single document content from `/api/documents/{id}` endpoint
2. Markdown rendered using react-markdown library with remark plugins (GitHub Flavored Markdown support)
3. Rendered content includes: headers (h1-h6), paragraphs, lists (ordered/unordered), tables, blockquotes, inline code, code blocks, links, images
4. Code blocks have syntax highlighting using Prism.js or similar (supports TypeScript, Python, JavaScript, YAML, JSON)
5. Each code block includes "Copy" button in top-right corner
6. Content area has max-width constraint (1280px per UX spec) for readability
7. Typography uses Inter font with 1.5 line height for body text

### Story 3.3: Detail View - Table of Contents

As a **user**,
I want **Table of Contents sidebar in Detail view**,
so that **I can quickly jump to specific sections in long documents**.

**Acceptance Criteria:**

1. TOC automatically generated from document headings (H2 and H3 levels included)
2. TOC displayed in left sidebar (256px width per UX spec, collapsible on narrow screens)
3. TOC items clickable - clicking scrolls to corresponding section with smooth animation (400ms per UX spec)
4. Active section highlighted in TOC based on scroll position (heading currently visible at top of viewport)
5. TOC shows hierarchical structure (H2 as parent, H3 nested with indentation)
6. TOC sticky positioned (stays visible while scrolling main content)
7. Empty state: TOC hidden if document has <3 headings

### Story 3.4: Architecture View - Tech Stack Display

As a **user**,
I want **Architecture view to display tech stack and system design documents**,
so that **I can understand technical decisions and architecture**.

**Acceptance Criteria:**

1. Architecture view fetches documents where doc_type = 'architecture'
2. View prioritizes displaying "tech-stack.md" prominently if it exists (top section)
3. Markdown tables in architecture docs rendered correctly (tech stack typically documented as table)
4. Document cards similar to Scoping view but with architecture-specific icons (🏗️)
5. If "architecture.md" exists, display as featured card (larger, full-width) before other architecture docs

### Story 3.5: Mermaid Diagram Rendering

As a **user**,
I want **Mermaid diagrams to render as visual diagrams instead of code blocks**,
so that **I can understand system architecture visually**.

**Acceptance Criteria:**

1. Markdown rendering (from Story 3.2) detects code blocks with language = `mermaid`
2. Mermaid.js library integrated to render diagrams client-side
3. Supported diagram types: flowchart, sequence diagram, class diagram, ER diagram, C4 diagram
4. Diagrams rendered with default Mermaid theme (light mode per UX spec)
5. **Graceful fallback:** If Mermaid rendering fails (invalid syntax, unsupported diagram type), display original code block with warning message: "⚠️ Diagram could not be rendered. Showing code instead."
6. **Timebox: 1.5 days max** - If basic integration works in 1 day, spend 0.5 day on error handling. If complex (2+ days), implement fallback only and defer full rendering

### Story 3.6: Epics View - List Display

As a **user**,
I want **Epics view to show list of all epics with status indicators**,
so that **I can see project epic structure at a glance**.

**Acceptance Criteria:**

1. Epics view fetches documents where doc_type = 'epic' from API
2. Epics displayed as list (table or card list) with columns: Epic Title, Status, Story Count, Last Modified
3. Status displayed with color-coded badge: Draft (gray), Dev (blue), Done (green) per UX spec
4. Story Count calculated from relationships table (count child documents where relationship_type = 'contains')
5. Clicking epic row navigates to Detail view showing full epic content
6. Epics sorted by filename/number (e.g., Epic 1, Epic 2, Epic 3) for logical sequence
7. Status rollup widget displayed at top: "X epics total | Y draft, Z in dev, W done"

### Story 3.7: Inter-Document Link Navigation

As a **user**,
I want **markdown links to other documents to navigate within BMADFlow**,
so that **I can explore related documentation without leaving the dashboard**.

**Acceptance Criteria:**

1. Markdown rendering (Story 3.2) detects links to `.md` files (e.g., `[Architecture](../architecture.md)`)
2. Link resolver service maps file paths to document IDs in database
3. Links rewritten to navigate to Detail view route: `/detail/{document_id}` using React Router Link component
4. Clicking inter-document link navigates within SPA (no page reload)
5. Breadcrumb navigation updated to show: Project > Current View > Document Title
6. External links (http/https) open in new tab with `target="_blank" rel="noopener"`
7. Broken links (reference non-existent document) styled differently (red text) with tooltip: "Document not found"

### Story 3.8: Sync Status Indicator

As a **user**,
I want **persistent sync status indicator in dashboard header**,
so that **I always know if my documentation is up-to-date**.

**Acceptance Criteria:**

1. Header displays last sync timestamp (e.g., "Last synced: 2 hours ago")
2. "Sync Now" button in header triggers manual sync
3. Button disabled during active sync with loading spinner
4. Sync progress displayed as toast notification in top-right (per UX spec): "Syncing... 45 of 100 documents"
5. Toast notification updates every 2 seconds via polling sync-status endpoint
6. On sync complete, toast shows success message: "✓ Sync complete. Extracted 95 of 100 documents." (auto-dismisses after 4 seconds)
7. On sync failure, toast shows error with "Retry" action
8. Dashboard content auto-refreshes after successful sync (React Query cache invalidation)

---

## Epic 4: Epic-Story Relationship Visualization

**Epic Goal:** Build table/list visualization of epic-to-story relationships with status color-coding and click-to-navigate. Interactive graph with zoom/pan as stretch goal if Week 5 timeline permits.

### Story 4.1: Epic-Story Relationship Data API

As a **frontend developer**,
I want **API endpoint returning epic-story relationship graph data**,
so that **I can build visualization components**.

**Acceptance Criteria:**

1. GET `/api/projects/{id}/relationships` endpoint returns JSON representing epic-story graph
2. Response format: `{ nodes: [ {id, title, type: 'epic'|'story', status, document_id} ], edges: [ {source_id, target_id, type: 'contains'} ] }`
3. Nodes include extracted epic/story data (title from extracted_epics/extracted_stories, status for color-coding)
4. Edges derived from relationships table (epic → stories links)
5. Endpoint includes optional query param `?epic_id=` to filter graph to single epic and its stories
6. Response cached with 5-minute TTL (Redis cache)

### Story 4.2: Epic-Story Table View

As a **user**,
I want **table view showing epics and their related stories**,
so that **I can understand project structure without needing graph visualization**.

**Acceptance Criteria:**

1. Epics view includes toggle button: "Graph View" | "Table View" (Table is default for POC)
2. Table view displays hierarchical list: Epic row (bold, status badge) followed by indented Story rows
3. Table columns: Title, Status, Type (Epic/Story), Last Modified
4. Epic rows expandable/collapsible (clicking epic toggles visibility of child stories)
5. All epics expanded by default on initial load
6. Status displayed with color-coded badge (draft=gray, dev=blue, done=green)
7. Clicking any row (epic or story) navigates to Detail view for that document

### Story 4.3a: Basic Graph Visualization (MVP)

As a **user**,
I want **interactive graph visualization of epic-story relationships**,
so that **I can visually explore project structures**.

**Acceptance Criteria:**

1. React Flow library integrated into Epics view
2. Graph renders nodes (epics + stories) and edges (contains relationships)
3. Nodes color-coded by status: Draft (gray), Dev (blue), Done (green)
4. Hierarchical layout (epics at top, stories below)
5. Clicking node navigates to Detail view for that document
6. Basic zoom/pan with mouse wheel and drag
7. Handles 50 nodes without performance issues

**Stretch Goal - Ship only if Week 5 timeline permits (2 days):**

### Story 4.3b: Graph Polish and Advanced Features (Stretch)

As a **user**,
I want **polished graph visualization with advanced interactions**,
so that **exploring complex relationships is effortless**.

**Acceptance Criteria:**

1. Minimap in bottom-right corner
2. "Center View" reset button
3. Node labels with smart truncation
4. Force-directed layout option (user toggle)
5. Hover tooltips showing full title
6. Smooth animations and transitions

### Story 4.4: Status Rollup Widget

As a **user**,
I want **status summary widget in Epics view**,
so that **I can see project health at a glance**.

**Acceptance Criteria:**

1. Widget displayed prominently in Epics view (top-right sidebar per UX spec)
2. Widget shows: "X epics | Y stories"
3. Widget shows status breakdown: "Z draft, W in dev, V done"
4. Status counts derived from extracted_epics and extracted_stories tables
5. Widget shows percentage complete: "(V/Y stories done = X%)"
6. Visual progress bar shows completion percentage (green fill)

### Story 4.5: Search/Filter Across Epics and Stories

As a **user**,
I want **search functionality to find specific epics or stories by keyword**,
so that **I can quickly locate information without browsing entire graph**.

**Acceptance Criteria:**

1. Search input field at top of Epics view (consistent with Scoping view from Story 3.1)
2. Search filters both epics and stories by title match (case-insensitive substring search)
3. Table view: Filtered results show matching epics/stories, other rows hidden
4. Graph view: Filtered results highlight matching nodes (dimmed/grayed out non-matches)
5. Search is client-side for POC (filters already-loaded data, no server query)
6. Clear button (X icon) in search input resets filter
7. Debounced input (300ms delay) to avoid re-filtering on every keystroke

### Story 4.6: Error Handling and Resilience

As a **user**,
I want **graceful error handling throughout the dashboard**,
so that **temporary failures don't break my workflow**.

**Acceptance Criteria:**

1. All API calls wrapped in try/catch with user-friendly error messages
2. Network errors show toast notification: "⚠️ Connection lost. Retrying..." with auto-retry (exponential backoff, max 3 attempts)
3. GitHub sync failures display actionable errors: "GitHub rate limit exceeded. Try again in X minutes or add Personal Access Token."
4. Extraction failures (low confidence score) marked visually in Detail view: "⚠️ Some information may be inaccurate. Extracted with low confidence."
5. Missing documents (broken inter-doc links) show placeholder: "Document not found. It may have been deleted or moved."
6. Empty states throughout: No projects, no documents, no epics, no stories (with helpful next-step guidance)
7. All errors logged to Sentry (error tracking) for debugging

### Story 4.7: Pilot User Feedback Collection and Documentation

As a **pilot user**,
I want **feedback form to rate my BMADFlow experience and access to user documentation**,
so that **the PM can measure POC success and I can learn how to use the platform effectively**.

**Acceptance Criteria:**

1. Feedback button in dashboard header (icon: 💬)
2. Modal form with fields: (1) Overall rating (1-5 stars), (2) "Is BMADFlow better than GitHub?" (Yes/No), (3) Favorite feature (dropdown), (4) Improvement suggestions (textarea)
3. Form submits to `/api/feedback` endpoint, stored in database
4. Thank you message after submission: "Thank you! Your feedback helps us improve BMADFlow."
5. PM can export feedback via admin endpoint: GET `/api/admin/feedback?project_id=` (CSV export)
6. Feedback form accessible from all views (persistent header button)
7. Help button (icon: ❓) in dashboard header opens user documentation modal or sidebar
8. User documentation includes: (a) Quick start guide with screenshots, (b) How to sync repositories, (c) How to navigate the 4 views, (d) How to interpret status colors, (e) FAQ section
9. Documentation written in markdown, rendered using existing MarkdownRenderer component
10. Documentation stored in `/docs/user-guide.md` file, loaded dynamically by frontend

---

## Epic and Story Files

All epics and stories from this PRD have been extracted into individual files for development workflow:

**Epic Files Location:** `docs/epics/`
- [Epic 1: Foundation, GitHub Integration & Dashboard Shell](epics/epic-1-foundation-github-dashboard.md)
- [Epic 2: LLM-Powered Content Extraction](epics/epic-2-llm-content-extraction.md)
- [Epic 3: Multi-View Documentation Dashboard](epics/epic-3-multi-view-dashboard.md)
- [Epic 4: Epic-Story Relationship Visualization](epics/epic-4-epic-story-visualization.md)

**Story Files Location:** `docs/stories/`
- Total: 33 story files (Stories 1.1 through 4.7)
- Naming pattern: `story-{epic}-{number}-{title-slug}.md`
- Each story links to its parent epic and includes complete acceptance criteria

**Status:** All epic and story files extracted and ready for development (2025-10-01)

---

## Checklist Results Report

### PM CHECKLIST VALIDATION - COMPREHENSIVE ASSESSMENT

**Overall PRD Completeness:** 95% (Excellent)
**MVP Scope Appropriateness:** Just Right (with clear stretch goals)
**Readiness for Architecture Phase:** **READY** ✅

### Category Analysis Table

| Category | Status | Critical Issues | Notes |
|----------|--------|-----------------|-------|
| 1. Problem Definition & Context | **PASS** (100%) | None | Comprehensive background from brief, clear goals, quantified metrics |
| 2. MVP Scope Definition | **PASS** (95%) | Minor: Future enhancements not explicitly listed in separate section | Out-of-scope clearly defined in requirements |
| 3. User Experience Requirements | **PASS** (98%) | None | Detailed UI goals with POC realism |
| 4. Functional Requirements | **PASS** (98%) | None | 20 FRs covering all MVP features, testable, well-scoped |
| 5. Non-Functional Requirements | **PASS** (95%) | None | 11 NFRs including performance, privacy, testing |
| 6. Epic & Story Structure | **PASS** (97%) | None | 4 epics, 33 stories, refined sizing, clear dependencies |
| 7. Technical Guidance | **PASS** (100%) | None | Extensive technical assumptions, stack specified |
| 8. Cross-Functional Requirements | **PASS** (90%) | None | Integration and operational requirements complete |
| 9. Clarity & Communication | **PARTIAL** (85%) | Moderate: Communication plan added to Next Steps | Well-written, clear structure |

**Overall Assessment:** 96% Complete - Ready for Architecture Phase

### Final Decision

✅ **READY FOR ARCHITECT**

**Confidence Level:** 95%

**Justification:**
- All 20 functional requirements well-defined and testable
- 32 stories with clear acceptance criteria, realistic sizing, and explicit dependencies
- Technical guidance extensive (technology stack, architecture direction, risk mitigation)
- MVP scope appropriate with stretch goals and fallback plans
- Minor gaps (communication plan) addressed in Next Steps section
- No blockers preventing Architect from proceeding

---

## Next Steps

### Communication Plan

**Weekly Sync Meetings:**
- **Cadence:** Every Monday 10am, 30 minutes
- **Attendees:** PM (John), Developer, Pilot User Representative
- **Agenda:** Progress review, blockers, upcoming week plan, scope adjustments

**Decision Authority Matrix:**

| Decision Type | Authority | Escalation Path |
|---------------|-----------|-----------------|
| Story AC clarification | Developer → PM | N/A |
| Technical implementation details | Developer/Architect | PM (if impacts timeline) |
| Scope changes (add/remove stories) | PM → DSI Sponsor | BMAD Core (if methodology impact) |
| Timeline extension (>1 week slip) | PM → DSI Sponsor | Go/No-Go review |
| POC Go/No-Go decision | DSI Sponsor + PM | BMAD Core input |

**Pilot User Engagement:**
- **Onboarding:** Week 1 - Share PRD, schedule kickoff demo
- **Check-ins:** Bi-weekly starting Week 3
  - Week 3: Demo Scoping + Detail views, gather feedback
  - Week 5: Demo full dashboard + visualization, gather feedback
  - Week 6: Final feedback collection via Story 4.7 form

**PRD Approval Sign-Off:**
- **Required Approvals:**
  - DSI Team Sponsor: Approve budget, timeline, POC approach
  - BMAD Core Team: Confirm methodology alignment
  - Pilot Users: Confirm availability and willingness to test
- **Timeline:** Obtain approvals within 3 business days before architecture phase

---

### Phase 2 Roadmap

**High-Priority Enhancements (Post-POC, If Greenlit):**

1. **Authentication & Team Management** (Priority: CRITICAL) - User accounts, team workspaces, role-based access
2. **Private Repository Support** (Priority: CRITICAL) - GitHub OAuth, private repo access
3. **Automated Synchronization** (Priority: HIGH) - Scheduled sync, webhook-based updates
4. **Semantic/AI Search** (Priority: HIGH) - RAG-based Q&A, natural language queries
5. **Advanced Graph Visualization** (Priority: MEDIUM) - Multiple layouts, dependency types, filtering

**Additional Enhancements (Q2-Q3 2026):**

6. Multi-Repository Aggregation
7. Neo4j Graph Database
8. CI/CD Automation
9. Mobile Responsive Design
10. High Test Coverage (80%+ backend, 70%+ frontend, E2E tests)
11. Enhanced Monitoring & Analytics
12. Multi-Methodology Support (SAFe, Scrum@Scale)

**Enterprise Features (Year 2):**

13. SSO & Advanced RBAC
14. Compliance & Audit Logs (SOC2, HIPAA)
15. Public API & Integrations (Jira, Linear, Slack)
16. Performance Optimization (CDN, caching, distributed architecture)

---

### UX Expert Prompt

Sally, we need your UX expertise to validate and enhance our vision:

**Task:** Review the completed PRD (especially UI Goals section and Epic 3 stories) and create detailed UI/UX specification building on the front-end-spec.md already drafted.

**Focus Areas:**
1. Validate the 4-view dashboard structure aligns with user workflows
2. Design high-fidelity mockups for critical screens (Figma)
3. Specify component behavior details for Epic 3 implementation
4. Review Story 3.1-3.8 acceptance criteria - flag any UX concerns

**Deliverable:** Updated front-end-spec.md with Figma mockup links and detailed component specifications

**Timeline:** 3-5 days (parallel with Architect's work)

---

### Architect Prompt

Winston, we're ready for you to design the complete system architecture:

**Task:** Create comprehensive fullstack architecture document (docs/architecture.md) based on this PRD, front-end-spec.md, and your technical expertise.

**Key Requirements:**
1. Validate Technical Assumptions - Review technology stack choices, confirm or suggest alternatives
2. Design Database Schema - Expand Story 1.2 into complete schema
3. Define API Contracts - RESTful endpoint specifications for all stories
4. Architecture Diagrams - System context, components, deployment, data flow
5. Address Technical Risks - Mitigation plans for LLM accuracy, GitHub rate limits, Mermaid rendering, graph scalability
6. Development Setup - Docker Compose details, local workflow, testing strategy
7. Review Critical Stories - Flag any underspecified requirements

**Deliverable:** Complete architecture.md document ready for Developer to begin Epic 1

**Timeline:** 3-5 days (Week 0 before development starts)

---

### POC Execution Timeline

**Week 0 (Architecture Phase):** 3-5 days
- Architect creates architecture.md
- UX Expert refines front-end-spec.md
- PM obtains PRD approvals
- Developer sets up development environment

**Week 1 (Epic 1):** Foundation, GitHub Integration & Dashboard Shell - 8 stories

**Week 2 (Epic 2):** LLM-Powered Content Extraction - 9 stories

**Week 3 (Epic 3 - Part 1):** Multi-View Dashboard Must-Haves - 4 stories
- **Milestone:** First pilot user testing

**Week 4 (Epic 3 - Part 2):** Multi-View Dashboard Should-Haves - 4 stories

**Week 5 (Epic 4 - Part 1):** Relationship Visualization Must-Haves - 6 stories
- **Milestone:** Feedback collection begins

**Week 6 (Epic 4 - Part 2 + Polish):** Stretch Goals & Refinement - 2 stories
- **Milestone:** POC Demo & Go/No-Go Decision

---

### Success Criteria Review

**POC Must Achieve (Go Criteria):**

1. ✅ **Extraction Reliability:** 90%+ accuracy on BMAD documents
2. ✅ **UX Improvement:** 80%+ pilot users rate 4-5 stars
3. ✅ **Graph Visualization Value:** 70%+ users find relationships useful
4. ✅ **Technical Stability:** Core features work without critical bugs
5. ✅ **Performance Adequate:** Sync <5-10 min, dashboard <3 sec

**No-Go Indicators:**
- Extraction accuracy <70%
- <60% positive user feedback
- Critical bugs blocking testing
- Timeline slips >2 weeks

**Go Decision Leads To:**
- 8-12 week industrialization sprint (Q1 2026)
- Team expansion to 2-3 developers
- Beta launch preparation (Q2 2026)
- $72K ARR target by Q4 2026

---

**PRD Version:** 1.0
**Status:** Ready for Architecture Phase
**Next Review:** Post-Architecture (after Winston completes architecture.md)
**Owner:** John (PM)
**Approvers:** DSI Sponsor, BMAD Core Team, Pilot Users
