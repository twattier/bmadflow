# BMADFlow - Use Case Specifications

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

## 4. Key Functionalities

### 4.1 Project Management
**Purpose**: Centralize and organize BMAD Method projects

- **Dashboard**: Overview of all managed projects with key metrics
- **Project List**: Display all existing projects with basic information
- **Create Project**: Initialize a new project with configuration
- **View Project Details**: Access comprehensive project information including:
  - AI chatbot interface for documentation querying
  - ProjectDocs listing with selection capability
  - Configuration management (name, description, linked ProjectDocs)
  - Each Project references 1+ ProjectDocs (name, description, GitHub link)

### 4.2 Documentation Synchronization
**Purpose**: Keep local documentation in sync with GitHub repositories

- **Manual Import Trigger**: On-demand synchronization from selected ProjectDocs
- **Sync Status Display**: Shows last synchronization date vs. last GitHub commit date
- **File Scanning**: Automatically scans and imports all text-based formats:
  - Markdown (.md)
  - CSV (.csv)
  - YAML (.yaml, .yml)
  - Text (.txt)
  - JSON (.json)
  - Other text formats managed by Docling python library
- **Database Storage**: Imported files stored in database for querying and indexing

### 4.3 Documentation Explorer
**Purpose**: Visual navigation and rendering of documentation files

- **File Tree Navigation**: 
  - Display hierarchical folder structure
  - File selection interface
  
- **Content Rendering**: Optimized display based on file type:
  - **Markdown**: Enhanced rendering with proper formatting
    - Support for Mermaid diagrams
    - Syntax highlighting for code blocks
  - **CSV**: Table visualization
  - **Other text files**: Raw text display with formatting
  
- **Cross-Document Navigation**: 
  - Support for relative links between markdown documents
  - Seamless navigation between referenced files

### 4.4 RAG Knowledge Base
**Purpose**: Intelligent indexing for semantic search capabilities

- **Vector Database**: PostgreSQL with pgvector extension
- **Intelligent Pipeline**: 
  - Document serialization
  - Hybrid chunking strategy (optimized for technical documentation)
  - Embedding generation and storage
- **Scope**: Per ProjectDocs (granular knowledge base management)

### 4.5 RAG Chatbot
**Purpose**: Natural language interface for documentation querying

- **Conversation Management**:
  - View previous conversations
  - Start new conversation sessions
  - Conversation history persistence

- **LLM Selection**: 
  - Choose from configured LLM models
  - Model options defined in global configuration

- **Query Capabilities**:
  - Default: Query knowledge base using RAG
  - Provides responses with source document links
  - from a source document link can show it directly at the right location (header link)
  - Context-aware answers based on project documentation

- **Agent Architecture**: 
  - Tool-based agent with knowledge base access
  - Source attribution and citation

### 4.6 Global Configuration
**Purpose**: System-wide settings and integrations management

- **LLM Models Management**:
  - View configured models
  - Add new models from various providers:
    - OpenAI
    - Google Gemini
    - LiteLLM
    - Ollama (local models)
  - Model configuration parameters

---

## 5. Data Requirements

### 5.1 Data Types

| Data Category | Description | Criticality Level |
|---------------|-------------|-------------------|
| **Technical Documentation** | Markdown files, architecture diagrams, code examples, process descriptions | **Public** - No restrictions |
| **Project Metadata** | Project names, descriptions, GitHub repository URLs | **Public** - No restrictions |
| **Configuration Files** | YAML, JSON configuration files from projects | **Public** - No restrictions |
| **User Interactions** | Chatbot conversation history, query logs | **Public** - No personal data |
| **LLM Configuration** | Model names, API endpoints (no credentials stored in public POC) | **Public** - Configuration only |

### 5.2 Data Criticality Assessment

**Personal Data (GDPR)**: ❌ None
- No personal information processed
- No user identification required for POC

**Sensitive Data (OIV/LPM)**: ❌ None
- All documentation is public or intended for public sharing
- No business-sensitive information

**Confidential Data**: ❌ None
- Open-source POC with public documentation
- No access control requirements for this version

**Data Security Level**: **Open** - Public documentation only

---

## 6. Benefits

### 6.1 Qualitative Benefits

1. **Improved Documentation Discoverability**
   - Centralized access to all BMAD Method project documentation
   - Unified interface replacing scattered GitHub repository navigation

2. **Reduced Information Search Time**
   - AI-powered semantic search vs. manual file browsing
   - Natural language queries instead of keyword-based GitHub search
   - Cross-project search capabilities

3. **Enhanced Onboarding Experience**
   - New developers can quickly understand existing projects
   - Pattern discovery across multiple projects
   - Self-service documentation access

4. **Better Understanding of BMAD Method Patterns**
   - Ability to query and compare approaches across projects
   - Identification of best practices through documentation analysis
   - Knowledge sharing and standardization support

5. **Improved Developer Experience**
   - Single point of access for all project documentation
   - Enhanced markdown rendering with diagrams
   - Conversational interface for documentation queries

### 6.2 Quantitative Metrics

**Note**: As a POC, quantitative gains are not measured at this stage.

**Current Scope**:
- **Projects**: ~10 BMAD Method projects
- **Users**: 3 active developers
- **Use Case**: Internal tooling and proof-of-concept validation

**Potential Future Metrics** (if scaled beyond POC):
- Time saved per documentation search
- Reduction in duplicate questions/issues
- Onboarding time reduction for new developers
- Documentation query success rate

---

## 7. Solution Orientation

### 7.1 Security Approach: **OPEN**

**Rationale**:
- All data processed is **public documentation** (GitHub public repositories)
- No personal data, no business-sensitive information
- No OIV (Critical Infrastructure) requirements
- No GDPR constraints

**Implications**:
- ✅ Use of external LLM providers allowed (OpenAI, Gemini)
- ✅ Public hosting of POC on GitHub
- ✅ No data sovereignty requirements
- ✅ Simplified architecture without strict isolation

### 7.2 Solution Type: **SPECIFIC SOLUTION**

**Classification**: Custom solution combining multiple patterns

**Rationale**:
- **Not a pure RAG solution** because:
  - Requires sophisticated file explorer interface
  - Project and ProjectDocs management layer
  - Multiple rendering engines (markdown, CSV, diagrams)
  - GitHub synchronization logic
  
- **Not a pure Agentic solution** because:
  - Heavy emphasis on UI/UX for documentation browsing
  - Complex data management beyond conversation
  - Integration with external systems (GitHub)
  
- **Specific Solution** characteristics:
  - **RAG component**: Knowledge base + chatbot for querying
  - **Document management system**: Sync, storage, organization
  - **Visualization layer**: File explorer, markdown rendering
  - **Integration layer**: GitHub API, multiple LLM providers

### 7.3 Technical Architecture Implications

**Stack Alignment**:
- **Backend**: FastAPI (Python)
- **RAG**: Docling for RAG document processing
- **Agentic**: Pydantic for structured data and agent framework
- **Database**: PostgreSQL with pgvector extension
- **Deployment**: Monorepo on GitHub

**Key Technical Constraints**:
1. **GitHub Integration**: Reliable sync mechanism with rate limiting
2. **Multi-format Support**: Robust parsing for various text formats
3. **Markdown Rendering**: Support for Mermaid diagrams and relative links
4. **Vector Search**: Optimized chunking strategy for technical docs
5. **Multi-LLM Support**: Abstraction layer for different providers

---
