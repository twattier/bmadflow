# Introduction

## Starter Template or Existing Project

**N/A - Greenfield project**

This is a greenfield full-stack application built from scratch using a monorepo structure with Docker Compose orchestration. The PRD specifies all technology choices explicitly (PostgreSQL+pgvector, FastAPI, React with Vite), requiring no starter template. This specificity allows optimal architecture for unique requirements while avoiding template constraints.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-06 | 1.0 | Initial architecture document | Winston - Architect |

---

## Document Overview

This document outlines the complete fullstack architecture for **BMADFlow**, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

This unified approach combines what would traditionally be separate backend and frontend architecture documents, streamlining the development process for modern fullstack applications where these concerns are increasingly intertwined.

**📚 Developer Quick Start**: This architecture document is complemented by the [`/docs/context/`](context/) directory containing production-ready code examples, best practices, and implementation patterns for all major technologies. These technical references are integrated into the [Development Workflow](#development-workflow) and [Coding Standards](#coding-standards) sections.

**Context**: BMADFlow is a locally-deployed documentation hub for BMAD Method projects that provides:
- GitHub documentation synchronization with intelligent metadata extraction
- Visual file tree explorer with markdown/CSV/Mermaid rendering
- AI-powered RAG chatbot with source attribution and header anchor navigation
- Project and document management with sync status tracking
- Dashboard metrics and activity monitoring

**Architectural Approach**:
- **Structure**: Monorepo with shared TypeScript types enabling type-safe frontend/backend communication
- **Frontend**: React 18+ with TypeScript, Vite build tool, shadcn/ui Dashboard template
- **Backend**: FastAPI (Python 3.11+) monolithic REST API with OpenAPI/Swagger documentation
- **Database**: PostgreSQL 15+ with pgvector extension (unified vector database for RAG)
- **RAG Pipeline**: Docling (document processing) → Ollama API client (embeddings via localhost:11434) → pgvector (storage/search)
- **Deployment**: Docker Compose orchestration supporting Full Docker (frontend/backend/database containerized) or Hybrid (frontend/backend local, database in Docker) modes
- **Testing**: Comprehensive pyramid with pytest (70%+ backend coverage), React Testing Library (component tests), Playwright (E2E tests), Playwright MCP integration

**External Dependencies**:
- **Ollama Service**: Pre-existing Ollama instance running at localhost:11434 with nomic-embed-text model (dim 768) - **NOT included in BMADFlow Docker Compose**
- **GitHub API**: Public repository access (unauthenticated initially; token authentication can be added if rate limits become an issue during POC)
- **LLM Providers**: Optional cloud LLM APIs (OpenAI, Google Gemini, LiteLLM) configured via environment variables

**Key Architecture Decisions**:
- **Local-First Design**: NFR5 mandates localhost deployment, eliminating cloud infrastructure complexity for POC while enabling rapid iteration
- **External Ollama Dependency**: Backend connects to existing Ollama service (localhost:11434); FR32 validates connectivity on startup with clear error if unavailable
- **Vector Dimension Lock-In**: Ollama nomic-embed-text (dim 768) fixed for POC—changing requires database recreation (acceptable trade-off documented in PRD)
- **Monorepo Justification**: Enables atomic commits across stack, shared TypeScript types prevent duplication, single deployment pipeline
- **Docker Scope**: BMADFlow services only (frontend, backend, PostgreSQL, pgAdmin); Ollama managed externally

**Docker Services (BMADFlow Stack)**:
1. **Frontend** (React + Vite) - Port 3000 (default, configurable via FRONTEND_PORT)
2. **Backend** (FastAPI) - Port 8000 (default, configurable via BACKEND_PORT)
3. **PostgreSQL + pgvector** (ankane/pgvector:latest) - Port 5432 (default, configurable via POSTGRES_PORT)
4. **pgAdmin** (database admin) - Port 5050 (default, configurable via PGADMIN_PORT)

**Note:** All port numbers shown in this document are default values. Actual ports are configurable via .env environment variables to avoid conflicts with existing services on the developer machine.

**Related Documentation**:
- Requirements: [docs/prd.md](docs/prd.md) - 65 requirements (44 FR + 21 NFR), 36 stories across 6 epics
- UX Design: [docs/ux-specification.md](docs/ux-specification.md) - User flows, component library, accessibility
- Project Context: [docs/brief.md](docs/brief.md) - Business need, target users (3 users, ~10 projects)
- **Implementation Guides**: [docs/context/](context/) - Code examples, patterns, and best practices for all technologies
- **QA Documentation**: [docs/qa/](../qa/) - Comprehensive testing guides, quality gates, and test architecture

---
