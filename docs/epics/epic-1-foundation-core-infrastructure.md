# Epic 1: Foundation & Core Infrastructure

## Epic Overview

**Epic ID**: Epic 1
**Epic Name**: Foundation & Core Infrastructure
**Status**: In Progress - 5 Done, 0 In Progress (5/6 stories)
**Created**: 2025-10-06
**Last Updated**: 2025-10-06
**Priority**: Critical (Foundation)

## Epic Goal

Establish the foundational project structure, containerized services, database with migrations, basic REST API scaffolding, and a simple frontend landing page. This epic validates the complete development workflow and deployment pipeline end-to-end while delivering a testable "Hello BMADFlow" application.

## Epic Description

This epic creates the complete technical foundation that all subsequent epics will build upon. By the end of this epic, developers will have:

- A working monorepo with frontend and backend directories
- PostgreSQL with pgvector extension running in Docker
- FastAPI backend with Alembic migrations and OpenAPI documentation
- React frontend with shadcn/ui Dashboard template and Tailwind CSS
- Docker Compose orchestration supporting both Full Docker and Hybrid deployment modes
- End-to-end integration validated with a "Hello BMADFlow" application

**Success Criteria**:
- User can run `docker-compose up` and see "Hello BMADFlow" message in browser at `http://localhost:3000`
- Backend health check endpoint returns 200 OK
- Database connection established with pgvector extension enabled
- Hot reload works in both Full Docker and Hybrid modes

## Business Value

Establishes technical foundation enabling rapid parallel development across teams. Validates deployment pipeline early, reducing risk of integration issues later. Provides working reference implementation for all subsequent stories.

## Dependencies

**Prerequisites**:
- Developer machine with Docker Desktop installed
- Python 3.11+ installed (for Hybrid mode)
- Node.js 18+ installed (for Hybrid mode)
- Ollama service running locally with `nomic-embed-text` model

**Blocks**:
- All subsequent epics (Epic 2-6) depend on this foundation

## Stories

This epic contains **6 stories**:

1. **✅ [Story 1.1: Initialize Monorepo Structure](../stories/1.1.initialize-monorepo-structure.md)** - **Done** ✅
   - Create backend and frontend directories with package management
   - Configure code quality tools (Black, Ruff, ESLint, Prettier)
   - Create root README with setup instructions

2. **✅ [Story 1.2: Setup PostgreSQL with pgvector and pgAdmin](../stories/1.2.setup-postgresql-pgvector-pgadmin.md)** - **Done** ✅
   - Create docker-compose.yml with PostgreSQL and pgAdmin services
   - Enable pgvector extension
   - Configure Docker volumes for data persistence
   - **QA Gate**: PASS (Quality Score: 100/100) - [Gate File](../qa/gates/1.2-setup-postgresql-pgvector-pgadmin.yml)

3. **✅ [Story 1.3: Initialize FastAPI Backend with Alembic Migrations](../stories/1.3.initialize-fastapi-backend-alembic.md)** - **Done** ✅
   - Create FastAPI application with main.py entry point
   - Configure Alembic for database migrations with async support
   - Implement health check endpoint `/api/health` with database connectivity validation
   - **QA Gate**: PASS (Quality Score: 100/100) - [Gate File](../qa/gates/1.3-initialize-fastapi-backend-alembic.yml)

4. **✅ [Story 1.4: Initialize React Frontend with shadcn/ui Dashboard Template](../stories/1.4.initialize-react-frontend-shadcn.md)** - **Done** ✅
   - Initialize React 18+ with TypeScript using Vite
   - Install shadcn/ui Dashboard template
   - Create "Hello BMADFlow" landing page
   - **QA Gate**: PASS (Quality Score: 100/100) - [Gate File](../qa/gates/1.4-initialize-react-frontend-shadcn.yml)

5. **✅ [Story 1.5: Create Docker Compose for Full Docker Deployment](../stories/1.5.docker-compose-full-deployment.md)** - **Done** ✅
   - Add frontend and backend services to docker-compose.yml
   - Configure service dependencies and health checks
   - Create Dockerfiles for frontend and backend
   - **QA Gate**: PASS (Quality Score: 95/100) - [Gate File](../qa/gates/1.5-docker-compose-full-deployment.yml)

6. **✅ [Story 1.6: Implement "Hello BMADFlow" End-to-End Integration](../stories/1.6.hello-bmadflow-e2e-integration.md)** - Draft
   - Create backend endpoint `/api/hello`
   - Frontend fetches and displays API response
   - Playwright MCP test validates full stack
   - Update README with deployment instructions

## Technical Approach

### Architecture Decisions

**Monorepo Structure**:
```
bmadflow/
├── backend/          # Python FastAPI application
│   ├── app/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # React TypeScript application
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

**Docker Compose Services**:
- `db` (PostgreSQL + pgvector)
- `backend` (FastAPI)
- `frontend` (React + Vite)
- `pgadmin` (Database admin UI)

**Technology Stack** (from [Tech Stack](../architecture/tech-stack.md)):
- **Frontend**: React 18+, TypeScript 5.x+, Vite 5.x+, shadcn/ui, Tailwind CSS
- **Backend**: Python 3.11+, FastAPI 0.110+, SQLAlchemy 2.x+, Alembic
- **Database**: PostgreSQL 15+ with pgvector (ankane/pgvector Docker image)
- **Deployment**: Docker Compose

### Integration Points

**Frontend → Backend**:
- Frontend calls `http://localhost:8000/api/hello`
- CORS configured to allow `http://localhost:3000` origin

**Backend → Database**:
- SQLAlchemy async connection pool
- Connection string: `postgresql+asyncpg://bmadflow:password@db:5432/bmadflow`

**Developer → Docker Compose**:
- `docker-compose up` starts all services
- Volume mounts enable hot reload for both frontend and backend

## Testing Strategy

**Unit Tests**: Not required for Epic 1 (infrastructure setup)

**Integration Tests**:
- Backend health check endpoint test
- Database connectivity test

**E2E Tests**:
- Playwright MCP test: Navigate to http://localhost:3000, verify "Hello BMADFlow" message displayed
- Screenshot capture for validation

**Manual Testing**:
- Full Docker mode: `docker-compose up` → verify "Hello BMADFlow" in browser
- Hybrid mode: Start Docker services → Run backend locally → Run frontend locally → verify "Hello BMADFlow"

## Definition of Done

- [ ] All 6 stories completed with acceptance criteria met
- [ ] Full Docker mode working: `docker-compose up` displays "Hello BMADFlow"
- [ ] Hybrid mode working: Local frontend/backend + Docker DB displays "Hello BMADFlow"
- [ ] Backend health check endpoint returns 200 OK
- [ ] PostgreSQL accessible via pgAdmin at http://localhost:5050
- [ ] pgvector extension enabled and verified
- [ ] Hot reload working in both deployment modes
- [ ] README.md includes setup instructions for both modes
- [ ] Playwright MCP test passes with screenshot captured
- [ ] Code quality tools configured and passing (Black, Ruff, ESLint, Prettier)

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Docker resource constraints | High | Medium | Provide Hybrid mode as alternative; document minimum Docker Desktop settings (4+ CPUs, 8GB RAM) |
| Port conflicts (5432, 8000, 3000, 5050) | Medium | Medium | All ports configurable via .env file; document conflict resolution |
| Ollama not installed/running | High | High | Clear error message on backend startup; document prerequisite in README |
| pgvector extension not available | High | Low | Use ankane/pgvector Docker image (includes extension pre-installed) |
| CORS issues between frontend/backend | Medium | Medium | Configure CORS middleware in Story 1.3; test in Story 1.6 |

## Related Documentation

- **PRD Epic 1**: [docs/prd.md#epic-1-foundation--core-infrastructure](../prd.md#epic-1-foundation--core-infrastructure)
- **Architecture**: [docs/architecture.md](../architecture.md)
- **Tech Stack**: [docs/architecture/tech-stack.md](../architecture/tech-stack.md)
- **Deployment**: [docs/architecture/deployment.md](../architecture/deployment.md)
- **Source Tree**: [docs/architecture/source-tree.md](../architecture/source-tree.md)
- **Development Workflow**: [docs/architecture/development-workflow.md](../architecture/development-workflow.md)
- **Testing Strategy**: [docs/architecture/testing-strategy.md](../architecture/testing-strategy.md)
- **Early Test Architecture**: [docs/qa/early-test-architecture.md](../qa/early-test-architecture.md)

## Story Sequence

**Sequential Dependencies**:
1. Story 1.1 (Monorepo) → Story 1.2 (Database) → Story 1.3 (Backend) → Story 1.4 (Frontend) → Story 1.5 (Docker Compose Full) → Story 1.6 (E2E Integration)

**Critical Path**:
- Story 1.2 must complete before Story 1.3 (backend needs database)
- Story 1.3 must complete before Story 1.6 (E2E needs backend endpoint)
- Story 1.4 must complete before Story 1.6 (E2E needs frontend)

**Parallelization Opportunities**:
- Stories 1.3 and 1.4 can be developed in parallel after Story 1.2 completes
- Story 1.5 can begin once Stories 1.3 and 1.4 are complete

## Acceptance Criteria (Epic Level)

1. **Full Docker Deployment**:
   - [ ] Run `docker-compose up` successfully starts all 4 services (db, backend, frontend, pgadmin)
   - [ ] Navigate to http://localhost:3000 displays "Hello BMADFlow" message
   - [ ] Backend API at http://localhost:8000/api/hello returns `{"message": "Hello BMADFlow", "status": "ok"}`
   - [ ] pgAdmin accessible at http://localhost:5050
   - [ ] All services show healthy status: `docker-compose ps`

2. **Hybrid Deployment**:
   - [ ] Run `docker-compose -f docker-compose.hybrid.yml up -d` starts database and pgAdmin
   - [ ] Run backend locally: `uvicorn app.main:app --reload` starts successfully
   - [ ] Run frontend locally: `npm run dev` starts successfully
   - [ ] Navigate to http://localhost:3000 displays "Hello BMADFlow" message

3. **Database Validation**:
   - [ ] PostgreSQL container running and accessible
   - [ ] pgvector extension enabled: `SELECT * FROM pg_extension WHERE extname = 'vector';` returns row
   - [ ] Database persists data across container restarts (Docker volume working)

4. **Code Quality**:
   - [ ] Backend: `black --check .` and `ruff check .` pass
   - [ ] Frontend: `npm run lint` passes
   - [ ] No linting errors in codebase

5. **Documentation**:
   - [ ] README.md includes Full Docker deployment instructions
   - [ ] README.md includes Hybrid deployment instructions
   - [ ] README.md documents prerequisites (Docker, Python, Node.js, Ollama)
   - [ ] .env.example file created with all required environment variables

6. **Testing**:
   - [ ] Playwright MCP test successfully captures screenshot of "Hello BMADFlow" page
   - [ ] Backend health check endpoint returns 200 OK

## Notes

- This epic focuses on **infrastructure only** - no business logic implemented yet
- **Hot reload is critical** for developer experience - ensure volume mounts work correctly
- **Ollama prerequisite** must be clearly communicated - backend will fail to start without it in later epics (not required for Epic 1)
- **Port configurability** via .env prevents conflicts on developer machines
- **Playwright MCP integration** validates our E2E testing approach early

## Timeline Estimate

**Total Effort**: 12-24 hours (6 stories × 2-4 hours each)

**Story Breakdown**:
- Story 1.1: 2-3 hours
- Story 1.2: 2-3 hours
- Story 1.3: 2-4 hours
- Story 1.4: 2-4 hours
- Story 1.5: 2-3 hours
- Story 1.6: 2-4 hours

**Recommended Approach**: Complete sequentially to validate each layer before building the next

---

## Story Drafting Summary

**Story Drafting Completed**: 2025-10-06

All 6 stories for Epic 1 have been drafted and are ready for implementation:

| Story | File | Size | Status |
|-------|------|------|--------|
| 1.1 | [1.1.initialize-monorepo-structure.md](../stories/1.1.initialize-monorepo-structure.md) | 8.2K | ✅ **Done** |
| 1.2 | [1.2.setup-postgresql-pgvector-pgadmin.md](../stories/1.2.setup-postgresql-pgvector-pgadmin.md) | 15K | ✅ **Done** (QA: PASS 100/100) |
| 1.3 | [1.3.initialize-fastapi-backend-alembic.md](../stories/1.3.initialize-fastapi-backend-alembic.md) | 17K | ✅ **Done** (QA: PASS 100/100) |
| 1.4 | [1.4.initialize-react-frontend-shadcn.md](../stories/1.4.initialize-react-frontend-shadcn.md) | 13K | ✅ Draft |
| 1.5 | [1.5.docker-compose-full-deployment.md](../stories/1.5.docker-compose-full-deployment.md) | 14K | ✅ Draft |
| 1.6 | [1.6.hello-bmadflow-e2e-integration.md](../stories/1.6.hello-bmadflow-e2e-integration.md) | 16K | ✅ Draft |

**Story Quality**:
- All stories include clear acceptance criteria with checkboxes
- Comprehensive Dev Notes extracted from architecture documentation
- Source references: `[Source: architecture/filename.md#section]` format
- Testing guidance for each story
- Tasks/Subtasks breaking down implementation steps

**Validation**:
- Story 1.1: Validated and **Done** ✅
- Story 1.2: PO Validated (9/10 readiness) → Implemented → QA Gate **PASS** (100/100) → **Done** ✅
- Story 1.3: PO Validated (10/10 readiness, 71/71 criteria) → Implemented → QA Gate **PASS** (100/100) → **Done** ✅

**Implementation Notes**:
- Story 1.2: Dev agent handled port conflicts adaptively (5432 → 5434), fixed pgAdmin email validation
- Story 1.2: QA applied 3 quality improvements (removed obsolete version, fixed .env.example port references, corrected README password docs)
- Story 1.3: Dev agent delivered exceptional quality with modern async patterns, perfect Black/Ruff compliance
- Story 1.3: QA applied 1 quality improvement (updated .env.example for consistency with backend config)
- Story 1.4: Dev agent successfully initialized React 19.1, Vite 7.1, shadcn/ui with Tailwind CSS 3.4
- Story 1.4: QA Gate **PASS** (100/100) - Excellent implementation, all 5 ACs met, no refactoring needed

---

**Epic Status**: ✅ In Progress - 4 Done (4/6 stories complete, 67% progress)
**Next Action**: Validate and begin Story 1.5 (Create Docker Compose for Full Docker Deployment)
