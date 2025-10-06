# Source Tree

## Overview

BMADFlow uses a **monorepo structure** with separate frontend and backend directories, shared configuration at the root level, and Docker Compose orchestration. This document provides the complete source tree with annotations explaining the purpose of each directory and key files.

## Complete Directory Structure

```
bmadflow/                                    # Root monorepo directory
├── .git/                                    # Git repository
├── .gitignore                               # Git ignore patterns
├── README.md                                # Project documentation
├── docker-compose.yml                       # Full Docker orchestration
├── docker-compose.hybrid.yml                # Hybrid mode configuration
├── .env.example                             # Example environment variables
├── .env                                     # Local environment config (gitignored)
│
├── docs/                                    # Project documentation
│   ├── brief.md                             # Project brief
│   ├── prd.md                               # Product Requirements Document
│   ├── ux-specification.md                  # UX/UI specification
│   ├── architecture.md                      # Architecture root document
│   ├── architecture/                        # Sharded architecture sections
│   │   ├── introduction.md
│   │   ├── high-level-architecture.md
│   │   ├── tech-stack.md
│   │   ├── database-schema.md
│   │   ├── data-models.md
│   │   ├── api-specification.md
│   │   ├── backend-architecture.md
│   │   ├── frontend-architecture.md
│   │   ├── source-tree.md
│   │   ├── deployment.md
│   │   ├── development-workflow.md
│   │   ├── testing-strategy.md
│   │   ├── coding-standards.md
│   │   ├── error-handling.md
│   │   ├── security-performance.md
│   │   └── monitoring.md
│   ├── context/                             # Implementation patterns & examples
│   │   ├── backend/
│   │   │   ├── fastapi-patterns.md
│   │   │   └── ...
│   │   ├── frontend/
│   │   │   ├── shadcn-components.md
│   │   │   └── ...
│   │   ├── database/
│   │   │   ├── postgresql-pgvector-patterns.md
│   │   │   └── ...
│   │   └── deployment/
│   │       ├── docker-compose-patterns.md
│   │       └── ...
│   ├── stories/                             # User stories
│   │   ├── story-1-1-initialize-monorepo.md
│   │   ├── story-1-2-setup-postgres.md
│   │   └── ...
│   └── prd/                                 # Sharded PRD sections (if applicable)
│
├── backend/                                 # Python FastAPI backend
│   ├── Dockerfile                           # Backend Docker image
│   ├── requirements.txt                     # Python dependencies
│   ├── requirements-dev.txt                 # Dev dependencies (pytest, black, etc.)
│   ├── pyproject.toml                       # Python project config (Black, Ruff)
│   ├── pytest.ini                           # Pytest configuration
│   ├── alembic.ini                          # Alembic configuration
│   ├── .env.example                         # Backend environment example
│   │
│   ├── alembic/                             # Database migrations
│   │   ├── env.py                           # Alembic environment
│   │   ├── script.py.mako                   # Migration template
│   │   └── versions/                        # Migration scripts
│   │       ├── 001_initial_schema.py
│   │       ├── 002_add_pgvector.py
│   │       └── ...
│   │
│   ├── app/                                 # Application code
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI app entry point
│   │   ├── config.py                        # Configuration (env vars)
│   │   ├── database.py                      # Database connection & session
│   │   │
│   │   ├── api/                             # API routes layer
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                      # Dependency injection helpers
│   │   │   └── v1/                          # API v1 routes
│   │   │       ├── __init__.py
│   │   │       ├── health.py                # Health check endpoint
│   │   │       ├── projects.py              # Project CRUD
│   │   │       ├── project_docs.py          # ProjectDoc CRUD + sync
│   │   │       ├── documents.py             # Document retrieval
│   │   │       ├── conversations.py         # Conversation management
│   │   │       ├── messages.py              # Message send/receive
│   │   │       ├── llm_providers.py         # LLM provider config
│   │   │       ├── search.py                # Vector search
│   │   │       └── dashboard.py             # Dashboard metrics
│   │   │
│   │   ├── services/                        # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── project_service.py
│   │   │   ├── project_doc_service.py       # Sync orchestration
│   │   │   ├── document_service.py
│   │   │   ├── github_service.py            # GitHub API integration
│   │   │   ├── rag_service.py               # RAG pipeline orchestration
│   │   │   ├── embedding_service.py         # Ollama embeddings
│   │   │   ├── vector_search_service.py     # pgvector search
│   │   │   ├── chatbot_service.py           # RAG chatbot
│   │   │   ├── llm_service.py               # LLM provider abstraction
│   │   │   └── dashboard_service.py
│   │   │
│   │   ├── repositories/                    # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py           # Generic CRUD
│   │   │   ├── project_repository.py
│   │   │   ├── project_doc_repository.py
│   │   │   ├── document_repository.py
│   │   │   ├── chunk_repository.py          # Vector search queries
│   │   │   ├── conversation_repository.py
│   │   │   ├── message_repository.py
│   │   │   └── llm_provider_repository.py
│   │   │
│   │   ├── models/                          # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # Base model class
│   │   │   ├── project.py
│   │   │   ├── project_doc.py
│   │   │   ├── document.py
│   │   │   ├── chunk.py                     # Vector embeddings
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   └── llm_provider.py
│   │   │
│   │   ├── schemas/                         # Pydantic request/response DTOs
│   │   │   ├── __init__.py
│   │   │   ├── common.py                    # Shared schemas (pagination, errors)
│   │   │   ├── project.py
│   │   │   ├── project_doc.py
│   │   │   ├── document.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   ├── llm_provider.py
│   │   │   └── search.py
│   │   │
│   │   ├── agents/                          # Pydantic agent framework
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py                # Abstract agent base
│   │   │   ├── rag_agent.py                 # RAG chatbot agent
│   │   │   ├── tools/                       # Agent tools
│   │   │   │   ├── __init__.py
│   │   │   │   ├── vector_search.py
│   │   │   │   ├── get_document.py
│   │   │   │   └── format_sources.py
│   │   │   └── prompts/                     # System prompts
│   │   │       ├── __init__.py
│   │   │       └── rag_system_prompt.py
│   │   │
│   │   └── utils/                           # Utility functions
│   │       ├── __init__.py
│   │       ├── logging.py                   # Structured logging
│   │       ├── github_utils.py
│   │       ├── markdown_utils.py            # Header anchor extraction
│   │       └── retry.py                     # Retry decorators
│   │
│   ├── tests/                               # Backend tests
│   │   ├── __init__.py
│   │   ├── conftest.py                      # Pytest fixtures
│   │   ├── unit/                            # Unit tests
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   └── utils/
│   │   ├── integration/                     # Integration tests
│   │   │   ├── api/
│   │   │   ├── database/
│   │   │   └── external/                    # GitHub, Ollama, LLM tests
│   │   └── fixtures/                        # Test data
│   │       ├── sample_projects.json
│   │       └── sample_markdown.md
│   │
│   └── scripts/                             # Utility scripts
│       ├── seed_data.py                     # Seed test data
│       ├── validate_ollama.py               # Validate Ollama setup
│       └── generate_types.py                # Generate TypeScript types from Pydantic
│
├── frontend/                                # React TypeScript frontend
│   ├── Dockerfile                           # Frontend Docker image
│   ├── package.json                         # NPM dependencies
│   ├── package-lock.json
│   ├── tsconfig.json                        # TypeScript configuration
│   ├── tsconfig.node.json                   # TypeScript for Node scripts
│   ├── vite.config.ts                       # Vite build configuration
│   ├── tailwind.config.js                   # Tailwind CSS configuration
│   ├── postcss.config.js                    # PostCSS configuration
│   ├── .eslintrc.json                       # ESLint configuration
│   ├── .prettierrc                          # Prettier configuration
│   ├── .env.example                         # Frontend environment example
│   ├── index.html                           # HTML entry point
│   │
│   ├── public/                              # Static assets
│   │   ├── favicon.ico
│   │   └── robots.txt
│   │
│   ├── src/                                 # Application source
│   │   ├── main.tsx                         # React entry point
│   │   ├── App.tsx                          # Root App component
│   │   ├── router.tsx                       # React Router configuration
│   │   ├── index.css                        # Global styles
│   │   │
│   │   ├── pages/                           # Route components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Projects.tsx
│   │   │   ├── ProjectOverview.tsx
│   │   │   ├── DocumentationExplorer.tsx
│   │   │   ├── Chat.tsx
│   │   │   ├── Configuration.tsx
│   │   │   └── NotFound.tsx
│   │   │
│   │   ├── components/                      # Reusable components
│   │   │   ├── ui/                          # shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── dropdown-menu.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   ├── toast.tsx
│   │   │   │   ├── toaster.tsx
│   │   │   │   ├── tooltip.tsx
│   │   │   │   └── ...
│   │   │   ├── layout/                      # Layout components
│   │   │   │   ├── AppShell.tsx             # Root layout
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Breadcrumb.tsx
│   │   │   └── common/                      # Shared components
│   │   │       ├── LoadingSpinner.tsx
│   │   │       ├── ErrorDisplay.tsx
│   │   │       ├── EmptyState.tsx
│   │   │       └── ConfirmDialog.tsx
│   │   │
│   │   ├── features/                        # Feature-specific components
│   │   │   ├── projects/
│   │   │   │   ├── ProjectCard.tsx
│   │   │   │   ├── ProjectList.tsx
│   │   │   │   ├── CreateProjectDialog.tsx
│   │   │   │   └── ProjectDocCard.tsx
│   │   │   ├── explorer/
│   │   │   │   ├── FileTreePanel.tsx
│   │   │   │   ├── ContentViewer.tsx
│   │   │   │   ├── MarkdownRenderer.tsx
│   │   │   │   ├── CSVViewer.tsx
│   │   │   │   ├── CodeViewer.tsx
│   │   │   │   ├── MermaidDiagram.tsx
│   │   │   │   └── TableOfContents.tsx
│   │   │   ├── chat/
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   ├── SourcePanel.tsx
│   │   │   │   ├── ConversationHistory.tsx
│   │   │   │   └── LLMProviderSelector.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── MetricCard.tsx
│   │   │   │   ├── ActivityFeed.tsx
│   │   │   │   └── WelcomeCard.tsx
│   │   │   └── configuration/
│   │   │       ├── LLMProviderTable.tsx
│   │   │       └── AddLLMProviderDialog.tsx
│   │   │
│   │   ├── api/                             # API layer
│   │   │   ├── client.ts                    # Axios instance
│   │   │   ├── hooks/                       # React Query hooks
│   │   │   │   ├── useProjects.ts
│   │   │   │   ├── useProjectDocs.ts
│   │   │   │   ├── useDocuments.ts
│   │   │   │   ├── useFileTree.ts
│   │   │   │   ├── useConversations.ts
│   │   │   │   ├── useMessages.ts
│   │   │   │   ├── useLLMProviders.ts
│   │   │   │   ├── useSearch.ts
│   │   │   │   └── useDashboard.ts
│   │   │   ├── services/                    # API service functions
│   │   │   │   ├── projectService.ts
│   │   │   │   ├── chatService.ts
│   │   │   │   └── ...
│   │   │   └── types/                       # TypeScript types (generated from backend)
│   │   │       ├── project.ts
│   │   │       ├── projectDoc.ts
│   │   │       ├── document.ts
│   │   │       ├── conversation.ts
│   │   │       ├── message.ts
│   │   │       └── ...
│   │   │
│   │   ├── store/                           # Zustand stores
│   │   │   ├── appStore.ts                  # Global app state
│   │   │   └── chatStore.ts                 # Chat-specific state
│   │   │
│   │   ├── hooks/                           # Custom React hooks
│   │   │   ├── useKeyboardShortcuts.ts
│   │   │   ├── useDebounce.ts
│   │   │   └── useLocalStorage.ts
│   │   │
│   │   ├── utils/                           # Utility functions
│   │   │   ├── cn.ts                        # className merger (Tailwind)
│   │   │   ├── formatters.ts                # Date/time formatters
│   │   │   ├── validators.ts
│   │   │   └── constants.ts
│   │   │
│   │   └── lib/                             # Third-party lib configurations
│   │       └── react-query.ts               # React Query config
│   │
│   └── tests/                               # Frontend tests
│       ├── setup.ts                         # Test setup
│       ├── components/                      # Component tests (React Testing Library)
│       │   ├── ProjectCard.test.tsx
│       │   └── ...
│       ├── hooks/                           # Hook tests
│       │   └── useProjects.test.ts
│       └── e2e/                             # Playwright E2E tests
│           ├── browse-documentation.spec.ts
│           ├── sync-project-doc.spec.ts
│           └── ai-chat.spec.ts
│
└── .bmad-core/                              # BMAD Method framework files
    ├── core-config.yaml                     # Project configuration
    ├── agents/                              # Agent personas
    │   ├── pm.yaml
    │   ├── architect.yaml
    │   ├── dev.yaml
    │   └── ...
    ├── tasks/                               # Reusable tasks
    ├── templates/                           # Document templates
    ├── checklists/                          # Validation checklists
    └── data/                                # Reference data
```

## Key Directory Explanations

### Root Level

**docker-compose.yml**
- Full Docker mode: All services containerized (frontend, backend, db, pgAdmin)
- Development use: `docker-compose up`

**docker-compose.hybrid.yml**
- Hybrid mode: Only database + pgAdmin in Docker
- Frontend/backend run locally for hot reload
- Development use: `docker-compose -f docker-compose.hybrid.yml up`

**.env / .env.example**
- Environment variable configuration
- Contains database credentials, API keys, port assignments
- `.env` is gitignored, `.env.example` is committed as template

### Backend Structure

**app/main.py**
- FastAPI application entry point
- CORS middleware configuration
- API route registration
- OpenAPI/Swagger documentation setup
- Startup validation (Ollama connectivity check)

**app/api/v1/**
- API route handlers (controllers)
- Request validation via Pydantic schemas
- Response serialization
- Thin layer: delegates to service layer

**app/services/**
- Core business logic
- External API integrations (GitHub, Ollama, LLMs)
- Multi-step workflow orchestration (sync pipeline, RAG query)
- Error handling and retry logic

**app/repositories/**
- Database query abstraction
- SQLAlchemy ORM operations
- Transaction management
- Optimized queries (joins, eager loading)

**app/models/**
- SQLAlchemy ORM models mapping to PostgreSQL tables
- Relationships, constraints, indexes
- pgvector column type for embeddings

**app/schemas/**
- Pydantic models for API contracts
- Request DTOs (validation)
- Response DTOs (serialization)
- OpenAPI schema generation

**app/agents/**
- Pydantic-based agent framework
- RAG agent with tool definitions
- System prompts for LLM interactions

**alembic/versions/**
- Database migration scripts
- Sequential versioned migrations
- Auto-generated via `alembic revision --autogenerate`

**tests/**
- Unit tests: Isolated logic testing with mocks
- Integration tests: Database, external APIs, full workflows
- Fixtures: Sample data for tests

### Frontend Structure

**src/pages/**
- Route-level components
- Page layout composition
- Route parameter handling
- Page-specific state management

**src/components/ui/**
- shadcn/ui component library
- Installed via `npx shadcn-ui@latest add <component>`
- Fully customizable, copied into project
- Built on Radix UI primitives (accessibility)

**src/components/layout/**
- AppShell: Root layout with sidebar, header, breadcrumbs
- Sidebar: Navigation with project context
- Header: Global actions, search, user menu
- Breadcrumb: Dynamic breadcrumb trail

**src/features/**
- Feature-specific components (projects, explorer, chat)
- Business logic encapsulation
- Composed into pages
- Reusable across pages if needed

**src/api/hooks/**
- React Query hooks for data fetching
- Automatic caching, refetching, error handling
- Mutation hooks for create/update/delete operations
- Optimistic updates

**src/api/types/**
- TypeScript type definitions shared from backend
- Generated from Pydantic schemas (via script)
- Type-safe API communication

**src/store/**
- Zustand stores for global state
- Lightweight alternative to Redux
- Persistent state (localStorage) for theme, selected project

**tests/e2e/**
- Playwright end-to-end tests
- Test critical user flows (browse, sync, chat)
- Playwright MCP integration for AI-assisted testing

### Documentation Structure

**docs/architecture/**
- Sharded architecture document sections
- Each section is a focused markdown file
- Assembled via `md-tree` tool if needed

**docs/context/**
- Implementation guides and patterns
- Code examples for common scenarios
- Best practices from library documentation (via context7 MCP)

**docs/stories/**
- User story markdown files
- Acceptance criteria, implementation notes
- Generated from PRD epics

## File Naming Conventions

**Backend (Python):**
- **Modules**: `snake_case.py` (e.g., `project_service.py`)
- **Classes**: `PascalCase` (e.g., `ProjectService`)
- **Functions**: `snake_case` (e.g., `get_project_by_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `EMBEDDING_DIM`)

**Frontend (TypeScript/React):**
- **Components**: `PascalCase.tsx` (e.g., `ProjectCard.tsx`)
- **Hooks**: `camelCase.ts` starting with `use` (e.g., `useProjects.ts`)
- **Utilities**: `camelCase.ts` (e.g., `formatters.ts`)
- **Types**: `camelCase.ts` or `PascalCase.ts` (e.g., `project.ts`)

**Configuration Files:**
- Standard names: `package.json`, `tsconfig.json`, `pyproject.toml`
- Hidden configs: `.eslintrc.json`, `.prettierrc`

## Import Path Conventions

**Backend:**
```python
# Absolute imports from app root
from app.services.project_service import ProjectService
from app.models.project import Project
from app.schemas.project import ProjectResponse
```

**Frontend:**
```tsx
// Absolute imports via @ alias (configured in tsconfig.json and vite.config.ts)
import { Button } from "@/components/ui/button";
import { useProjects } from "@/api/hooks/useProjects";
import { Project } from "@/api/types/project";
```

**Vite Alias Configuration:**
```ts
// vite.config.ts
export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
```

## Generated Files (Not Committed)

**Backend:**
- `__pycache__/` - Python bytecode
- `.pytest_cache/` - Pytest cache
- `*.pyc` - Compiled Python files
- `.coverage` - Coverage reports

**Frontend:**
- `node_modules/` - NPM dependencies
- `dist/` - Vite build output
- `.vite/` - Vite cache
- `coverage/` - Test coverage reports

**Shared:**
- `.env` - Local environment variables (use `.env.example` as template)
- `*.log` - Log files

## Version Control (.gitignore)

```gitignore
# Environment
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.coverage
htmlcov/
venv/
.venv/

# Node
node_modules/
dist/
.vite/
coverage/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Docker
volumes/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

## Related Documentation

- **High Level Architecture**: [high-level-architecture.md](high-level-architecture.md)
- **Backend Architecture**: [backend-architecture.md](backend-architecture.md)
- **Frontend Architecture**: [frontend-architecture.md](frontend-architecture.md)
- **Development Workflow**: [development-workflow.md](development-workflow.md)

---
