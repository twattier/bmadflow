# Tech Stack

This is the **DEFINITIVE** technology selection for the entire project. All development must use these exact technologies and versions. This table is the single source of truth derived from PRD Technical Assumptions.

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| **Frontend Language** | TypeScript | 5.x+ | Type-safe frontend development | Prevents runtime errors, enables IDE autocomplete, shares types with backend |
| **Frontend Framework** | React | 18+ | UI component library and rendering | Industry standard, extensive ecosystem, hooks-based functional components |
| **Build Tool** | Vite | 5.x+ | Frontend build and dev server | Fast HMR, optimized production builds, native ESM support |
| **UI Component Library** | shadcn/ui | Latest | Accessible component primitives | Requirement FR40-42; pre-built Dashboard template; WCAG 2.1 AA compliant - [Component patterns](docs/context/frontend/shadcn-components.md) |
| **CSS Framework** | Tailwind CSS | 3.x+ | Utility-first styling | Included with shadcn/ui; rapid styling without CSS files |
| **State Management** | Zustand | 4.x+ | Lightweight global state | Simpler than Redux; Context API acceptable alternative per PRD |
| **Routing** | React Router | 6.x+ | Client-side routing | Standard React routing solution; supports protected routes |
| **HTTP Client** | Axios | 1.x+ | API communication | Interceptors for auth tokens, request/response transformation |
| **Markdown Rendering** | react-markdown | 9.x+ | Markdown to React components | Requirement FR7; supports remark/rehype plugins |
| **Code Highlighting** | Prism.js (react-prism-renderer) | Latest | Syntax highlighting in code blocks | Supports JS/TS/Python/bash/JSON/YAML per PRD |
| **Mermaid Diagrams** | react-mermaid2 | Latest | Render Mermaid diagrams in markdown | Requirement FR7; supports flowchart/sequence/class diagrams |
| **File Tree** | react-arborist | Latest (React 18+ compatible) | Virtual file tree navigation | UX spec requirement; handles large trees efficiently |
| **Icons** | Lucide React | Latest | Icon library | Specified in UX spec; GitHub-inspired aesthetic |
| **Frontend Testing** | React Testing Library | Latest | Component unit tests | Requirement NFR19; testing best practices |
| **Backend Language** | Python | 3.11+ | Backend application development | Requirement; Docling/Pydantic compatibility |
| **Backend Framework** | FastAPI | 0.110+ | REST API framework | Auto OpenAPI docs (FR30); async support; Pydantic integration - [FastAPI patterns](docs/context/backend/fastapi-patterns.md) |
| **API Style** | REST | OpenAPI 3.0 | HTTP API with JSON | Requirement FR30; simpler than GraphQL for POC |
| **ASGI Server** | uvicorn | Latest | Production ASGI server for FastAPI | Standard FastAPI deployment; supports hot reload |
| **Database** | PostgreSQL | 15+ | Relational database + vector storage | Requirement FR20; pgvector extension support - [PostgreSQL+pgvector patterns](docs/context/database/postgresql-pgvector-patterns.md) |
| **Vector Extension** | pgvector | Latest | Vector similarity search | Requirement FR20; enables <500ms search (NFR4) |
| **Docker Image (DB)** | ankane/pgvector | latest | Pre-configured PostgreSQL+pgvector | Ensures pgvector availability; simplifies setup |
| **Database Migrations** | Alembic | Latest | Schema version control | Requirement FR29; auto-generates migrations from models |
| **ORM** | SQLAlchemy | 2.x+ | Database abstraction layer | Works with Alembic; async support for FastAPI |
| **Document Processing** | Docling | Latest | Document chunking and parsing | Requirement FR21; HybridChunker strategy |
| **Embedding Client** | ollama-python | Latest | Ollama API client library | Generates embeddings via localhost:11434 |
| **Embedding Model** | nomic-embed-text | dim 768 | Text embedding generation | **FIXED** for POC (FR22); vector dimension lock-in |
| **Agent Framework** | Pydantic | 2.x+ | Structured data and agents | Requirement FR28; type validation |
| **LLM Clients** | openai, google-generativeai, litellm | Latest | Multi-provider LLM support | FR11; optional cloud LLM integration |
| **HTTP Client (Backend)** | httpx | Latest | Async HTTP requests | GitHub API calls; LLM API calls |
| **Backend Testing** | pytest | Latest | Unit and integration tests | Requirement NFR18; 70%+ coverage target |
| **Test Coverage** | pytest-cov | Latest | Coverage reporting | Track 70%+ backend coverage |
| **E2E Testing** | Playwright | Latest | Browser automation testing | Requirement NFR19, NFR21; Playwright MCP integration |
| **Code Quality (Frontend)** | ESLint + Prettier | Latest | Linting and formatting | Consistent code style |
| **Code Quality (Backend)** | Black + Ruff | Latest | Linting and formatting | Python code consistency |
| **Containerization** | Docker + Docker Compose | Latest | Local deployment orchestration | NFR6; Full Docker and Hybrid modes - [Docker Compose patterns](docs/context/deployment/docker-compose-patterns.md) |
| **Database Admin** | pgAdmin | Latest | Web-based database explorer | Requirement FR33; localhost:5050 no auth |
| **IaC Tool** | Docker Compose YAML | N/A | Infrastructure as code for local | Defines services, networks, volumes |
| **CI/CD** | None (for POC) | N/A | Manual deployment | Not required per PRD; local development only |
| **Monitoring** | Structured Logging | N/A | Application logging | Python `logging` (backend), console (frontend) per PRD |
| **Logging (Backend)** | Python logging | Built-in | Structured JSON logs to stdout | PRD Application Logging section |
| **Logging (Frontend)** | console | Built-in | Browser console logs | Debug (dev), Error/Warn only (prod) |
| **File Storage** | PostgreSQL BLOB | Built-in | Document content storage | Requirement FR27; no separate object store needed |
| **Authentication** | None (for POC) | N/A | No user auth | Single-tenant POC per Known Constraints |

**Critical Notes:**
- **Vector Dimension Lock-In**: nomic-embed-text (dim 768) cannot be changed without recreating database—acceptable for POC per PRD Known Constraints
- **Ollama Prerequisite**: Developers must have Ollama running locally with `ollama pull nomic-embed-text` before starting backend
- **Port Configurability**: All service ports configurable via .env to avoid conflicts
- **No Production Deployment Tools**: CI/CD, monitoring services, and cloud infrastructure intentionally excluded for POC scope
- **Technical Documentation**: See [`/docs/context/`](context/) for implementation patterns, code examples, and best practices (referenced in Development Workflow and Coding Standards sections below)

---
