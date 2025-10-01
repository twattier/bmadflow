# Technical Assumptions

## Repository Structure: Monorepo

Use monorepo structure with workspace tooling (npm workspaces or Turborepo) to house frontend, backend, and shared packages in a single repository.

**Rationale:** Frontend and backend share TypeScript types, simplifies CI/CD for single-developer POC, easier code sharing.

## Service Architecture: Modular Monolith (Backend) + SPA (Frontend)

**Architecture Style:**
- **Backend:** Python FastAPI monolithic application with modular services (GitHub sync, LLM extraction, API endpoints)
- **Frontend:** React Single Page Application (SPA) deployed separately
- **Deployment:** Docker containers with Docker Compose (Kubernetes deferred to industrialization)

**Rationale:** Microservices add unnecessary complexity for POC; modular monolith provides boundaries without distributed system overhead.

## Testing Requirements: Pragmatic POC Approach

**Testing Pyramid for POC:**
- **Backend Unit Tests:** Critical extraction logic, API endpoints (pytest) - Target 50% coverage
- **Backend Integration Tests:** GitHub API integration, LLM extraction end-to-end
- **Frontend Unit Tests:** Smoke tests only (React Testing Library + Vitest) - Target 30% coverage
- **E2E Tests:** Manual testing with pilot users (automated E2E deferred)

**Highest Priority:** Manual validation of LLM extraction on 100 sample documents (accuracy measurement more important than coverage metrics for POC).

**Rationale:** POC timeline prioritizes feature delivery; pilot user validation substitutes for extensive automation; industrialization brings coverage to 80%+.

## Additional Technical Assumptions and Requests

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
