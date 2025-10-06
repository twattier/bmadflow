# BMADFlow - Project Brief

## 1. Contacts

**Business Owner**: Thierry - Product Owner, IT Department (DSI)

---

## 2. Business Profiles Concerned

**Primary Users**: 
- Developers working with Claude Code and BMAD Method framework
- Product Owners managing BMAD projects
- Technical architects consulting project documentation

**User Base**: 
- Estimated 3 active users
- Managing approximately 10 projects

---

## 3. Business Need Summary

BMADFlow addresses the challenge of centralizing and efficiently exploring technical documentation generated across multiple projects using Claude Code and the BMAD Method framework.

**Context**: The IT department generates extensive documentation for each project following the BMAD Method. This documentation is scattered across different GitHub repositories, making it difficult to:
- Discover existing documentation across projects
- Search for specific information quickly
- Understand patterns and best practices used across projects
- Onboard new team members on existing projects

**Solution**: BMADFlow provides a centralized platform that synchronizes documentation from GitHub repositories, enables intelligent exploration through a visual interface, and offers an AI-powered chatbot for natural language querying of project documentation.

**Nature**: This is a public proof-of-concept (POC) hosted on GitHub, not intended for commercialization but for internal tooling and potential open-source sharing.

---

## 4. Proposed Solution

BMADFlow provides a centralized platform that transforms how teams interact with BMAD Method documentation through three core capabilities:

### 1. Automated Documentation Synchronization
Instead of manually navigating multiple repositories, BMADFlow automatically imports and synchronizes documentation from configured GitHub sources. The platform uses a flexible configuration model:

- **Projects**: Logical groupings that represent a BMAD initiative (e.g., "E-commerce Platform", "Analytics Dashboard")
- **ProjectDocs**: Individual documentation spaces, where each links to a specific GitHub repository folder and belongs to exactly one Project
- **Flexibility**: A single Project can aggregate documentation from multiple sources by having multiple ProjectDocs (e.g., one ProjectDocs for backend repo, another for frontend repo, both under the same Project)

The synchronization engine:
- Scans and imports all text-based formats (Markdown, CSV, YAML, JSON, TXT) using the Docling Python library
- Displays sync status showing last synchronization vs. last GitHub commit
- Stores imported files in a local database for fast querying and indexing
- **Intelligent header anchor extraction**: Identifies relevant section headers for each chunk and stores as metadata for precise navigation
- Allows on-demand manual sync triggers for immediate updates

### 2. Enhanced Documentation Explorer
A visual file tree interface with intelligent rendering based on file type:

- **Markdown files**: Full rendering with Mermaid diagram support and syntax-highlighted code blocks
- **CSV files**: Clean table visualization for structured data
- **Other formats**: Formatted text display with proper styling
- **Cross-document navigation**: Relative links between markdown documents work seamlessly, enabling natural exploration of interconnected documentation

### 3. AI-Powered Knowledge Base & Chatbot
Natural language interface powered by RAG (Retrieval-Augmented Generation) and agentic frameworks:

- **Unified Vector Database**: Single PostgreSQL/pgvector database stores embeddings from all ProjectDocs with metadata tagging (Project ID, ProjectDocs ID)
- **RAG Document Processing**: Docling Python library handles document serialization, hybrid chunking strategy optimized for technical documentation, and embedding generation
- **Embedding Model**: Ollama with nomic-embed-text (dim 768) - fixed for POC to maintain vector dimension consistency
- **Agent Framework**: Pydantic provides structured data handling and agent architecture for tool-based interactions with the knowledge base
- **Multi-LLM Inference Support**: Choose from multiple providers:
  - OpenAI (GPT-4, GPT-3.5-turbo)
  - Google Gemini
  - LiteLLM (unified interface for multiple providers)
  - Ollama (local models like llama2, mistral, etc.)
- **Conversation Management**: Persistent chat history with context-aware responses
- **Smart Source Attribution**:
  - Responses include links to source documents with intelligent anchor navigation
  - During sync, identify and store header anchor for each chunk in metadata
  - Click source link → navigate to specific section (if anchor identified) or document root (fallback)
- **Per-Project Query Scope**: Chatbot accessed from Project page, queries filtered to that Project's ProjectDocs
- **Future Capability**: Architecture supports querying across ALL projects for cross-project pattern discovery

### Why This Solution Works

- **Zero manual maintenance**: Developers continue working in GitHub as normal; BMADFlow automatically stays synchronized
- **Flexible organization**: Projects can aggregate documentation from multiple repositories/folders by configuring multiple ProjectDocs under one Project
- **Unified knowledge base**: Single vector database enables future cross-project querying without architectural changes
- **Familiar interface**: Visual file tree and markdown rendering feel like working locally, but with cross-repository reach
- **Intelligent discovery**: Natural language queries replace manual searching, surfacing patterns and connections humans might miss
- **Smart navigation**: Precise section-level linking when possible, graceful fallback when not
- **Open & extensible**: Public POC architecture allows for community contribution and customization

### Differentiators from Existing Solutions
Unlike GitHub's repository-by-repository search or manual wiki documentation, BMADFlow provides a unified semantic layer over all project documentation while preserving the single source of truth in GitHub repositories.

---

## 5. MVP Scope

### Core Features (Must Have)

#### 1. Project & ProjectDocs Management
- **Dashboard**: Overview of all managed Projects with key metrics (last sync, number of docs, activity)
- **Project CRUD**: Create, view, update, and delete Projects
- **ProjectDocs Configuration**:
  - Link ProjectDocs to specific GitHub repository folders
  - Associate one or more ProjectDocs with each Project
  - Configure ProjectDocs metadata (name, description, GitHub link)
- **Sync Status Display**: Show last sync date vs. last GitHub commit date for each ProjectDocs

#### 2. Documentation Synchronization
- **Manual Sync Trigger**: On-demand synchronization button for selected ProjectDocs
- **Multi-Format Support**: Scan and import Markdown (.md), CSV (.csv), YAML (.yaml, .yml), Text (.txt), and JSON (.json) files
- **Database Storage**: Store imported files in PostgreSQL for querying and indexing
- **GitHub Integration**: Read-only access to public GitHub repositories via API (unauthenticated)
- **Intelligent Metadata Extraction**:
  - Identify and extract header anchors for each document chunk
  - Store anchor links in chunk metadata for precise navigation
  - Fallback to document root link if header anchor cannot be identified

#### 3. Documentation Explorer
- **File Tree Navigation**: Hierarchical folder structure display for each ProjectDocs
- **File Selection Interface**: Click to view file contents
- **Enhanced Markdown Rendering**:
  - Proper markdown formatting with syntax highlighting
  - Mermaid diagram support (critical for BMAD architecture docs)
  - Syntax-highlighted code blocks
- **CSV Table Visualization**: Clean table rendering for CSV files
- **Cross-Document Navigation**: Support relative links between markdown files with seamless navigation

#### 4. RAG Knowledge Base
- **Unified Vector Database**: Single PostgreSQL with pgvector extension storing all embeddings
- **Metadata Tagging**: Each embedding tagged with Project ID and ProjectDocs ID for query filtering
- **Document Processing Pipeline**:
  - Docling library integration for document serialization
  - Hybrid chunking strategy optimized for technical documentation
  - Ollama embedding generation using nomic-embed-text (dim 768) - fixed for POC
  - Header anchor extraction and metadata storage

#### 5. AI Chatbot Interface
- **Project-Scoped Access**: Chatbot available from Project detail page
- **Query Scope**: Default queries across ALL ProjectDocs under selected Project (filtered by Project ID)
- **Future Enhancement**: Optional filter to restrict to single ProjectDocs OR expand to all Projects
- **Conversation Management**:
  - View previous conversations (history list)
  - Start new conversation sessions
  - Persistent conversation history
- **LLM Selection Dropdown**: Choose inference provider before starting conversation:
  - OpenAI (GPT-4, GPT-3.5-turbo)
  - Google Gemini
  - LiteLLM
  - Ollama (local models)
- **RAG Query Capability**:
  - Default behavior: Query knowledge base using RAG with vector search
  - Natural language input
  - Responses with smart source document links
  - **Smart Source Navigation**:
    - Click source link → navigate to specific header section (if anchor metadata exists)
    - Fallback to document root (if anchor not identified during sync)
- **Agent Architecture**: Pydantic-based tool agent with knowledge base access and source attribution

#### 6. Global Configuration
- **LLM Models Management**:
  - View list of configured inference models
  - Add new models from providers: OpenAI, Google Gemini, LiteLLM, Ollama (local)
  - Store model configuration parameters (API endpoints, model names)
  - Note: For POC, API credentials managed via environment variables (not stored in UI)

#### 7. Playwright MCP Integration (Must Have)
- **Frontend Development Testing**:
  - MCP server integration to programmatically launch frontend
  - Automated screenshot capture during development
  - Console log monitoring and analysis
- **Manual Test Plan Generation**:
  - AI-assisted test scenario generation based on UI state
  - Screenshot-based regression detection
  - Clear test plans for manual validation
- **Developer Experience**: Enable rapid debugging and visual verification workflows

### Out of Scope for MVP

Deferred to Future Versions:
- Automated Scheduled Sync: Manual trigger only for MVP; no background scheduled syncing
- User Authentication & Multi-tenancy: Single deployment for internal team; no user login or access control
- Webhook Integration: No real-time sync on GitHub commits; manual trigger only
- Advanced Search Filters: Basic RAG search only; no complex filtering, date ranges, or faceted search
- ProjectDocs-Level Filtering: Chatbot queries entire Project; single ProjectDocs filtering deferred
- Cross-Project Queries: Chatbot scoped to single Project; cross-project querying deferred
- Document Editing: Read-only platform; no in-app editing of documentation
- Export Functionality: No bulk export or report generation features
- Mobile Optimization: Desktop-first UI; responsive design not prioritized
- Collaboration Features: No commenting, annotations, or sharing functionality
- Version History Tracking: No historical view of documentation changes over time
- Advanced Analytics Dashboard: Basic usage metrics only; no detailed analytics or reporting
- Custom Chunking Strategies: Use Docling defaults; no user-configurable chunking parameters
- Alternative Embedding Models: Fixed to Ollama nomic-embed-text for POC
- Multiple Vector Search Algorithms: Single default RAG approach; no algorithm comparison
- Real-time Collaboration: No multi-user simultaneous editing or viewing indicators

---

## 6. Technical Assumptions

### Technology Stack

#### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (latest stable)
- **API Style**: REST with OpenAPI/Swagger documentation
- **RAG Library**: Docling (for document processing, chunking, embeddings)
- **Agent Framework**: Pydantic (structured data, agent architecture)
- **Embedding Model**: Ollama with nomic-embed-text (dim 768) - fixed for POC to maintain vector dimension consistency

#### Database & Storage
- **Primary Database**: PostgreSQL 15+ with pgvector extension
- **Vector Database Architecture**: Single unified database storing embeddings from all ProjectDocs
- **Metadata Tagging**: Each embedding tagged with Project ID, ProjectDocs ID, and source document information
- **Vector Dimension**: Fixed at 768 dimensions (nomic-embed-text) - changing embedding model would require database recreation
- **Database Admin Tool**: pgAdmin (containerized) for database exploration and debugging
- **File Storage**: Database BLOB storage for imported documentation (POC simplicity)

#### Frontend
- **Framework**: React 18+ with TypeScript
- **UI Library**: shadcn/ui with dashboard template (provides navigation, layouts, and core components out of the box)
- **Markdown Rendering**: react-markdown with remark/rehype plugins
- **Mermaid Rendering**: mermaid.js integration for diagram rendering
- **Code Highlighting**: Prism.js or highlight.js for syntax highlighting
- **State Management**: React Context API or Zustand (lightweight)

#### External Integrations
- **GitHub API**: REST API v3 for repository access (read-only, public repos, unauthenticated)
- **LLM Providers for Inference**:
  - OpenAI API (GPT-4, GPT-3.5-turbo)
  - Google Gemini API
  - LiteLLM (unified interface for multiple providers)
  - Ollama (local models like llama2, mistral, etc.)
- **Embedding Provider**: Ollama only (nomic-embed-text) - fixed for POC

#### Development & Deployment
- **Package Manager**: pip + requirements.txt (backend), npm/yarn (frontend)
- **Containerization**: Docker + Docker Compose
- **Deployment Options** (POC runs on developer machine only):
  - Option 1 - Full Docker: All services containerized (frontend, backend, PostgreSQL+pgvector, pgAdmin)
  - Option 2 - Hybrid: Frontend and backend run as local services, PostgreSQL+pgvector and pgAdmin run in Docker containers
- **CI/CD**: Not required for POC; manual deployment on developer machine

### Testing Requirements

#### Backend Testing
- **Unit Tests**: pytest for business logic, RAG pipeline, data models
- **Integration Tests**: Test database operations, GitHub API integration, LLM provider connections, vector search
- **Test Coverage Target**: 70%+ for core business logic

#### Frontend Testing
- **Component Tests**: React Testing Library for UI components
- **Integration Tests**: Test user flows (explorer navigation, chatbot interaction)
- **E2E Tests**: Playwright for critical paths
- **Playwright MCP Integration** (Must Have):
  - MCP server for programmatic frontend launch
  - Automated screenshot capture and analysis
  - Console log monitoring and debugging
  - AI-assisted test plan generation

#### Manual Testing Convenience
- CLI scripts for seeding test data
- Test ProjectDocs configurations pointing to sample repositories (AgentLab, Magnet)
- Mock LLM responses for testing without API costs
- Playwright MCP for interactive testing and debugging workflows

### Additional Technical Assumptions

#### Deployment
- **Environment**: Local developer machine only (no cloud hosting for POC)
- **Deployment Options**:
  - Full Docker: `docker-compose up` starts all services
  - Hybrid Local: Run frontend/backend locally, docker-compose for database only
- **No Production Infrastructure**: POC validates approach before considering hosting
- **Database Persistence**: Docker volumes for PostgreSQL data persistence between restarts

#### Local Development Setup
- **Prerequisites**: Docker Desktop, Python 3.11+, Node.js 18+, Ollama installed locally with nomic-embed-text model
- **Database Management**: pgAdmin accessible at localhost:5050 for database exploration (no authentication for local POC)
- **Hot Reload**: Frontend and backend support hot reload for rapid development
- **Port Allocation**:
  - Frontend: localhost:3000 (or configured port)
  - Backend: localhost:8000 (FastAPI default)
  - PostgreSQL: localhost:5432
  - pgAdmin: localhost:5050

#### Data Volume Assumptions
- ~10 repositories with estimated 100-200 files per ProjectDocs
- Total documentation corpus: ~10-20 MB per ProjectDocs
- Vector database: ~100K-200K embeddings total across all ProjectDocs in unified database
- Chatbot conversations: ~100-500 conversations over POC period
- All data stored locally on developer machine

#### Performance Targets
- **Documentation Sync**: < 5 minutes per ProjectDocs (includes file import + Ollama embedding generation + metadata extraction + header anchor identification)
- **RAG Query Response**:
  - Cloud LLMs (OpenAI, Gemini): < 3 seconds end-to-end (vector search + inference)
  - Local Ollama Inference: < 10 seconds end-to-end (acceptable trade-off for cost savings and offline capability)
  - Performance varies based on selected LLM provider and model
- **Explorer Page Load**: < 2 seconds for file tree rendering
- **Markdown Rendering**: < 1 second for typical BMAD doc
- **Vector Search**: < 500ms for similarity search across unified database

---

## 7. Risks & Open Questions

### Key Risks

#### 1. RAG Quality & Relevance
- **Risk**: Chatbot responses may not be accurate or relevant enough for technical documentation queries
- **Description**: Technical documentation has unique structure (code snippets, architecture diagrams, specialized terminology) that may not chunk well or embed effectively. Docling's HybridChunker optimization should help, but needs validation with actual BMAD docs.
- **Impact**: Users abandon chatbot in favor of manual search if quality is poor
- **Mitigation**: Use Docling HybridChunker as designed; test with sample BMAD docs early; consider reranking post-POC

#### 2. Ollama Local Embedding & Inference Performance
- **Risk**: Local embedding generation and inference with Ollama may be slow or resource-intensive
- **Description**: Running embeddings and inference locally means performance depends on available hardware. Inference with local Ollama models expected to be slower than cloud APIs.
- **Impact**: Sync process takes longer; query response time up to 10 seconds vs. 3 seconds for cloud LLMs
- **Mitigation**: Keep POC scope small (~100-200 files per ProjectDocs); set user expectations for Ollama vs cloud LLM performance; accept slower response times as acceptable trade-off for cost and offline capability

#### 3. User Adoption & Engagement
- **Risk**: Target users don't actively use the platform despite development effort
- **Description**: Behavior change is hard; users may stick to familiar GitHub browsing habits
- **Impact**: POC fails validation; cannot measure success metrics or determine value
- **Mitigation**: Early user involvement; weekly check-ins; focus on clear time-saving wins

#### 4. LLM Provider Availability
- **Risk**: LLM provider outages during POC demonstrations
- **Description**: Reliance on external APIs (OpenAI, Gemini) or local Ollama introduces availability risk
- **Impact**: Chatbot becomes unavailable during critical demo or testing
- **Mitigation**: Support multiple LLM providers; Ollama as fallback for offline capability

#### 5. Header Anchor Extraction Accuracy
- **Risk**: Automated header anchor identification may fail for complex document structures
- **Description**: Not all chunks may have clear header associations; some documents may lack proper header structure
- **Impact**: Some source links fallback to document root instead of specific sections
- **Mitigation**: Graceful fallback to document root; acceptable for POC; can improve detection logic post-POC

### Known Limitations (Acceptable for POC)

#### GitHub API Rate Limits
- **Limitation**: Unauthenticated GitHub API has 60 requests/hour rate limit
- **Impact**: May slow down sync operations if many files in repository
- **Acceptable Because**: Manual sync only; low frequency; can add OAuth post-POC if needed

#### Vector Dimension Lock-In
- **Limitation**: Vector database fixed to 768 dimensions (nomic-embed-text)
- **Impact**: Cannot change embedding model without recreating entire database
- **Acceptable Because**: POC scope; can migrate to different embedding model post-POC if needed

#### pgAdmin Security
- **Limitation**: pgAdmin runs without authentication for local POC
- **Impact**: Database fully accessible from localhost
- **Acceptable Because**: Local developer machine only; no network exposure; not production deployment

### Technical Decisions (Resolved)
- ✅ Chunking Strategy: Use Docling HybridChunker as-is; keep simple for POC
- ✅ Embedding Model: Local embeddings with Ollama using nomic-embed-text (dim 768) - fixed for POC
- ✅ LLM Inference Providers: Multiple options (OpenAI, Gemini, LiteLLM, Ollama) - user selects per conversation
- ✅ Vector Database Architecture: Single unified database with metadata tagging for filtering
- ✅ Query Scope: Per-Project (aggregates across ProjectDocs); future: single ProjectDocs filter or cross-project queries
- ✅ Sync Frequency: Manual sync only for POC
- ✅ Source Navigation: Smart header anchor detection with fallback to document root
- ✅ Mermaid Complexity: No complex diagrams expected in POC scope
- ✅ Documentation Volume: ~100-200 files per ProjectDocs
- ✅ Query Types: Focus on project scope, architecture, epics/stories questions
- ✅ GitHub Authentication: Unauthenticated API access acceptable for POC
- ✅ PostgreSQL with pgvector: Sufficient for POC needs
- ✅ Deployment Architecture: Local developer machine with Docker (full or hybrid)
- ✅ Playwright MCP: Must-have for frontend testing and manual test plan generation

**No Critical Open Questions Remaining**

---

## 8. Next Steps

This Project Brief provides the foundation for BMADFlow development. The recommended next steps are:

1. **UI/UX Design**: Work with UX Expert to create detailed UI/UX specifications
2. **PRD Creation**: Expand this brief into a comprehensive Product Requirements Document
3. **Architecture Design**: Define technical architecture and implementation approach
4. **Development**: Begin iterative development using BMAD Method workflows

---

*Document created using BMAD-METHOD™ framework*