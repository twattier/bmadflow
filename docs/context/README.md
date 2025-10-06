# BMADFlow Context Documentation

This directory contains **external library documentation** retrieved from official sources via **MCP services** (context7, shadcn). Context docs provide production-ready patterns for FastAPI, shadcn/ui, PostgreSQL, pgvector, and Docker Compose.

> **🚀 NEW TO CONTEXT DOCS?** Read [HOW-TO-USE.md](HOW-TO-USE.md) for quick start guide
>
> **📋 MANDATORY POLICY**: [Code Examples Policy](../architecture/code-examples-policy.md) - Rules for using context docs

**🔑 Key Points**:
- **Source**: Populated by MCP services (context7, shadcn)
- **Purpose**: External library patterns, NOT BMADFlow-specific code
- **Authority**: Context docs override architecture examples
- **Maintenance**: Update when libraries upgrade or better patterns discovered

## 🎯 Quick Navigation

**Jump directly to what you need:**

| I'm working on... | Go to... | What's inside |
|-------------------|----------|---------------|
| 🔌 **API endpoints** | [FastAPI Patterns →](backend/fastapi-patterns.md) | Async routes, dependency injection, Pydantic models, error handling, background tasks |
| 🎨 **UI components** | [shadcn/ui Components →](frontend/shadcn-components.md) | Table, Card, Form, Dialog patterns, Dashboard layout, accessibility |
| 🔍 **Vector search** | [PostgreSQL+pgvector →](database/postgresql-pgvector-patterns.md) | SQLAlchemy async models, similarity search, indexing, 768-dim embeddings |
| 🐳 **Docker setup** | [Docker Compose →](deployment/docker-compose-patterns.md) | Multi-service orchestration, .env config, volumes, health checks |

## Directory Structure

```
/docs/context/
├── backend/
│   └── fastapi-patterns.md          # FastAPI async routes, dependency injection, Pydantic models
├── frontend/
│   └── shadcn-components.md         # shadcn/ui component patterns (Table, Forms, Cards, etc.)
├── database/
│   └── postgresql-pgvector-patterns.md  # PostgreSQL + pgvector with SQLAlchemy 2.x async
├── deployment/
│   └── docker-compose-patterns.md   # Multi-service orchestration, environment config, volumes
└── README.md                         # This file
```

## Purpose

These context documents serve as:

1. **Quick Reference**: Copy-paste ready code examples for common patterns
2. **Best Practices Guide**: Industry-standard approaches for each technology
3. **Onboarding Resource**: Help new developers understand the stack quickly
4. **Architecture Supplement**: Detailed implementation guidance referenced from [architecture.md](../architecture.md)

## How to Use

Each document is organized by topic with:

- **Code Examples**: Production-ready snippets you can adapt directly
- **Explanations**: Why certain patterns are recommended
- **Related Links**: Connections to official documentation and other context docs

### Backend Development

Start with [fastapi-patterns.md](backend/fastapi-patterns.md) for:
- Async API route patterns
- Database session management with dependency injection
- Pydantic request/response models
- Background tasks for long-running operations
- Repository pattern for database access

### Frontend Development

Start with [shadcn-components.md](frontend/shadcn-components.md) for:
- shadcn/ui component examples (Table, Card, Form, Dialog)
- Dashboard layout with sidebar navigation
- Form validation with react-hook-form and Zod
- Accessibility best practices (WCAG 2.1 AA)

### Database Development

Start with [postgresql-pgvector-patterns.md](database/postgresql-pgvector-patterns.md) for:
- pgvector setup and vector column definitions
- SQLAlchemy 2.x async models and queries
- Vector similarity search patterns (L2, cosine, inner product)
- HNSW and IVFFlat indexing strategies
- Performance optimization for 768-dimensional embeddings

### Deployment

Start with [docker-compose-patterns.md](deployment/docker-compose-patterns.md) for:
- Multi-service orchestration (frontend, backend, database)
- Environment variable configuration (.env patterns)
- Volume persistence for database data
- Health checks and service dependencies
- Development vs production configurations

## Integration with Architecture

These context documents are referenced directly in the [Tech Stack](../architecture.md#tech-stack) section of the architecture document. Each technology entry includes a link to its corresponding context documentation for deeper implementation guidance.

See the full [Context Documentation Reference](../architecture.md#context-documentation-reference) section in the architecture document for detailed usage patterns and common development scenarios.

## 📖 Development Workflow Examples

### Example 1: Building a New Feature (Project List Page)

**Task**: Create a project list page with table display

1. **UI Component** → Check [shadcn-components.md](frontend/shadcn-components.md)
   - Copy the `DocumentTableWithActions` example
   - Adapt for project data structure

2. **API Endpoint** → Check [fastapi-patterns.md](backend/fastapi-patterns.md)
   - Copy async route template
   - Use repository pattern for database access

3. **Database Query** → Check [postgresql-pgvector-patterns.md](database/postgresql-pgvector-patterns.md)
   - Use SQLAlchemy async query patterns
   - Implement repository `list_all()` method

**Result**: Complete feature with UI, API, and database layers following best practices

### Example 2: Implementing Vector Search

**Task**: Add semantic search to RAG chatbot

1. **Database Setup** → [postgresql-pgvector-patterns.md](database/postgresql-pgvector-patterns.md)
   - Create vector column with dimension 768
   - Configure HNSW index for performance
   - Use cosine distance for similarity

2. **API Endpoint** → [fastapi-patterns.md](backend/fastapi-patterns.md)
   - Create async search endpoint
   - Use Pydantic model for search request/response
   - Return top-k similar documents

3. **UI Integration** → [shadcn-components.md](frontend/shadcn-components.md)
   - Display search results in Card components
   - Show similarity scores and source attribution

**Result**: Production-ready vector search with optimized indexing

### Example 3: Setting Up Local Development

**Task**: Configure Docker services for development

1. **Docker Compose** → [docker-compose-patterns.md](deployment/docker-compose-patterns.md)
   - Use development configuration example
   - Configure .env file with port mappings
   - Set up volume persistence for database
   - Add health checks for service dependencies

2. **Backend Config** → [fastapi-patterns.md](backend/fastapi-patterns.md)
   - Configure CORS for localhost:3000
   - Set up database connection with async engine

3. **Database Init** → [postgresql-pgvector-patterns.md](database/postgresql-pgvector-patterns.md)
   - Enable pgvector extension
   - Run migrations with Alembic

**Result**: Fully functional local development environment

## 💡 Tips for Using Context Docs

✅ **DO:**
- Copy examples and adapt them to your specific use case
- Reference official documentation links for deep dives
- Use patterns as starting points, not rigid templates
- Check related context docs for cross-cutting concerns

❌ **DON'T:**
- Copy code blindly without understanding the pattern
- Skip error handling from examples
- Ignore performance guidance for production code
- Mix patterns from different architectural styles

## Maintenance

Context documents should be updated when:
- Major version upgrades occur for key technologies
- New architectural patterns emerge from development
- Best practices evolve in the industry
- MCP services provide updated documentation

To refresh documentation, use the context7 MCP service to retrieve the latest official docs and code examples.

## Related Documentation

- [Architecture Document](../architecture.md) - Full-stack architecture overview
- [PRD](../prd.md) - Product requirements and specifications
- [UX Specification](../ux-specification.md) - User experience design and component library
