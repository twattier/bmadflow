# BMADFlow Fullstack Architecture Document

> **Note**: This architecture document has been sharded into focused sections for easier navigation and maintenance. See the [Table of Contents](#table-of-contents) below for links to all sections.

## Document Overview

This document outlines the complete fullstack architecture for **BMADFlow**, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

**Context**: BMADFlow is a locally-deployed documentation hub for BMAD Method projects that provides:
- GitHub documentation synchronization with intelligent metadata extraction
- Visual file tree explorer with markdown/CSV/Mermaid rendering
- AI-powered RAG chatbot with source attribution and header anchor navigation
- Project and document management with sync status tracking
- Dashboard metrics and activity monitoring

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-06 | 1.0 | Initial architecture document | Winston - Architect |
| 2025-10-06 | 1.1 | Sharded document into focused sections | Winston - Architect |
| 2025-10-06 | 1.2 | Completed all architecture sections (7-17) | Winston - Architect |
| 2025-10-06 | 1.3 | Added Code Examples Policy for consistency | Winston - Architect |

---

## Table of Contents

This architecture document is organized into the following sections:

1. **[Introduction](architecture/introduction.md)** - Project introduction, starter template decision, and document overview
2. **[High Level Architecture](architecture/high-level-architecture.md)** - Technical summary, platform choice, repository structure, architecture diagrams, and architectural patterns
3. **[Tech Stack](architecture/tech-stack.md)** - Complete technology stack table (DEFINITIVE source of truth for all technology choices)
4. **[Database Schema](architecture/database-schema.md)** - PostgreSQL schema with pgvector, ERD, table definitions, indexes, and migration strategy
5. **[Data Models](architecture/data-models.md)** - SQLAlchemy ORM models, Pydantic API DTOs, and TypeScript type generation
6. **[API Specification](architecture/api-specification.md)** - RESTful API endpoints, request/response formats, OpenAPI documentation

7. **[Backend Architecture](architecture/backend-architecture.md)** - Service layer, repository pattern, RAG pipeline implementation, Pydantic agents, background jobs
8. **[Frontend Architecture](architecture/frontend-architecture.md)** - React component architecture, state management, routing, shadcn/ui integration
9. **Components** *(Covered in sections 7-8)* - Component details integrated into Backend and Frontend Architecture sections
10. **[Source Tree](architecture/source-tree.md)** - Complete directory structure and file organization
11. **[Deployment](architecture/deployment.md)** - Docker Compose setup (Full Docker + Hybrid modes), environment configuration
12. **[Development Workflow](architecture/development-workflow.md)** - Daily development tasks, common workflows, debugging, technical documentation reference
13. **[Testing Strategy](architecture/testing-strategy.md)** - Testing pyramid, backend/frontend/E2E tests, Playwright MCP integration, coverage goals
14. **[Coding Standards](architecture/coding-standards.md)** - Python/TypeScript conventions, critical rules, code review checklist
15. **[Error Handling](architecture/error-handling.md)** - Error patterns, HTTP status codes, retry logic, user-friendly messages
16. **[Security & Performance](architecture/security-performance.md)** - Security posture (POC), performance optimization, profiling
17. **[Monitoring](architecture/monitoring.md)** - Application logging, health checks, metrics, error tracking
18. **[Code Examples Policy](architecture/code-examples-policy.md)** - **MANDATORY**: Consistency rules for architecture/context docs, MCP service usage
19. **Checklist Results** *(TODO)* - Architecture validation checklist results (run `*execute-checklist` to generate)

---

## 🚨 CRITICAL: Code Examples Policy

> **MANDATORY READING**: All developers and AI agents MUST follow the [Code Examples Policy](architecture/code-examples-policy.md) when implementing features.
>
> **Key Rules:**
> 1. ✅ **Context docs are authoritative** - Implementation patterns in [docs/context/](context/) override architecture examples
> 2. ✅ **Check context docs first** - Before implementing, review relevant context documentation
> 3. ✅ **Use MCP services** - When context docs insufficient, use `context7` or `shadcn` MCP for latest patterns
> 4. ✅ **Maintain consistency** - All code examples in architecture MUST reference context docs
> 5. ✅ **Update context docs** - Document new patterns discovered during implementation
>
> **Violation of this policy leads to inconsistent codebase and architectural drift.**

---

## Quick Reference

### Key Architecture Decisions

- **Structure**: Monorepo with shared TypeScript types enabling type-safe frontend/backend communication
- **Frontend**: React 18+ with TypeScript, Vite build tool, shadcn/ui Dashboard template
- **Backend**: FastAPI (Python 3.11+) monolithic REST API with OpenAPI/Swagger documentation
- **Database**: PostgreSQL 15+ with pgvector extension (unified vector database for RAG)
- **RAG Pipeline**: Docling (document processing) → Ollama API client (embeddings via localhost:11434) → pgvector (storage/search)
- **Deployment**: Docker Compose orchestration supporting Full Docker or Hybrid deployment modes
- **Testing**: Comprehensive pyramid with pytest (70%+ backend coverage), React Testing Library, Playwright (E2E)

### External Dependencies

- **Ollama Service**: Pre-existing Ollama instance at localhost:11434 with nomic-embed-text model (dim 768) - **NOT included in BMADFlow Docker Compose**
- **GitHub API**: Public repository access (unauthenticated initially)
- **LLM Providers**: Optional cloud LLM APIs (OpenAI, Google Gemini, LiteLLM) configured via environment variables

### Related Documentation

- **Requirements**: [docs/prd.md](prd.md) - 65 requirements (44 FR + 21 NFR), 36 stories across 6 epics
- **UX Design**: [docs/ux-specification.md](ux-specification.md) - User flows, component library, accessibility
- **Project Context**: [docs/brief.md](brief.md) - Business need, target users (3 users, ~10 projects)
- **Implementation Guides**: [docs/context/](context/) - Code examples, patterns, and best practices (see [Code Examples Policy](architecture/code-examples-policy.md) for usage rules)

---

## Navigation

For detailed information on any architectural aspect, please refer to the specific section documents linked in the [Table of Contents](#table-of-contents) above.

To view the complete architecture as a single document, you can use the markdown-tree-parser tool to reconstruct it:

```bash
# Reconstruct full document (if needed)
md-tree implode docs/architecture docs/architecture-full.md
```

---

**Document Version**: 1.3
**Last Updated**: 2025-10-06
**Architecture Version**: v4 (Sharded)
**Status**: ✅ **COMPLETE** (18/19 sections) - Ready for implementation
**Consistency**: ✅ Enforced via [Code Examples Policy](architecture/code-examples-policy.md)
