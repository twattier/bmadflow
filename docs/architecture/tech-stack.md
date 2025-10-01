# Tech Stack

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
