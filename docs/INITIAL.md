# BMADFlow - Use Case Specification

## Executive Summary

**Project Type**: Proof of Concept (POC)  
**Context**: DSI initiative to improve documentation exploration and project visibility for BMAD Method projects  
**Objective**: Validate feasibility and value of an intelligent documentation visualization platform before potential industrialization

---

## 1. Contacts & Ownership

### Primary Contact
- **Name**: Thierry W
- **Role**: DSI - Operational Performance Team
- **Responsibility**: POC Sponsor and Business Owner

### Stakeholders
- DSI Operational Performance Team
- Project teams using BMAD Method
- Development teams using Claude Code

---

## 2. Target User Profiles

### Primary Users
- **Product Owners (PO)**: Main target users
- **Product Managers (PM)**: Main target users

### Secondary Users
- **Developers**: Can use for technical documentation reference
- **QA/Testers**: Can use for test specifications and quality gates

### User Needs
- Better navigation experience than raw GitHub markdown files
- Clear project status visibility
- Easy exploration of BMAD Method structured documentation
- Visual representation of epics and stories relationships

---

## 3. Business Need Summary

### Current Situation
Today, project teams using Claude Code and BMAD Method generate comprehensive structured documentation stored in GitHub repositories. However:
- Navigating markdown files directly in GitHub is cumbersome
- No consolidated view of project status
- Mermaid diagrams are not well rendered
- Difficult to get an overview across project phases (scoping, architecture, development)
- Hard to visualize epics-to-stories relationships
- Challenging to onboard new team members on projects

### Proposed Solution
BMADFlow is an intelligent documentation platform that:
- Synchronizes with public GitHub repositories
- Parses and understands BMAD Method documentation structure
- Extracts structured information using LLM capabilities
- Provides an intuitive dashboard with multiple views (scoping, architecture, epics)
- Visualizes project graphs and relationships
- Renders markdown content beautifully with proper Mermaid diagram support

### Activities Impacted
- Project documentation consultation
- Project status tracking
- Epic and story planning
- Team collaboration and knowledge sharing
- New team member onboarding

---

## 4. Key Functionalities

### F1: Project Management
**Description**: Add and manage projects by linking to public GitHub documentation repositories

**Details**:
- Input GitHub repository URL (e.g., `https://github.com/twattier/agent-lab/tree/main/docs`)
- Store project metadata (name, repository URL, last sync date)
- Support for multiple projects in the platform

### F2: GitHub Synchronization
**Description**: Manual synchronization with GitHub repository on demand

**Details**:
- "Synchronize" button on project dashboard
- Compare last sync timestamp with latest GitHub commit
- Parse entire documentation tree structure
- Extract markdown files and metadata
- Update database with latest content

**Structure to Parse**:
```
docs/
├── analysis/              # Scoping phase documents
├── prd.md                 # Product Requirements (sharded)
├── prd/                   # PRD sections
├── architecture.md        # Architecture (sharded)
├── architecture/          # Architecture sections
├── front-end-spec.md      # Frontend specification
├── epics/                 # Epic documents
├── stories/               # Story documents
├── qa/
│   ├── assessments/
│   └── gates/
```

### F3: Intelligent Content Extraction
**Description**: Parse and structure documentation using LLM capabilities

**Extraction Logic**:
- Split markdown files by headers (## level sections)
- Use LLM (OLLAMA) to understand and extract structured information
- Handle format variations gracefully (BMAD patterns with flexibility)

**Key Information to Extract**:

**For User Stories**:
- User Story format: "AS a [role] I want [feature] so that [benefit]"
- Acceptance Criteria
- Tasks / Subtasks
- Dev Notes
- QA Results
- Status: draft / dev / done

**For Epics**:
- Epic title and description
- Related stories
- Dependencies
- Status indicators

**For General Documents**:
- Section structure
- Key metadata
- Links and references

### F4: Project Dashboard - Multi-View Interface
**Description**: Comprehensive project visualization with 4 main views

#### View 1: Scoping Phase (📋 Qualification)
**Content**:
- Research & Analysis documents (from `docs/analysis/`)
  - Project Brief
  - Market Research Report
  - Competitor Analysis
  - Brainstorming Session Results
  - Initial Use Case Specification
- Core Project Documents
  - Product Requirements Document (PRD) - sharded view
  - Architecture Document - high-level overview
  - Frontend Specification

**Display**:
- Document cards with status indicators
- Purpose, key sections, and status for each document
- Navigation to detailed document view

#### View 2: Architecture (🏗️)
**Content**:
- High-level architecture overview
- Tech stack details
- API specifications
- Infrastructure and deployment strategy
- Complete sharded architecture sections

**Display**:
- Architecture diagrams (Mermaid)
- Component breakdown
- Technology choices with justifications

#### View 3: Epics View (📊)
**Content**:
- Interactive graph visualization of epics → stories relationships
- Epic status overview (draft / dev / done)
- Story count and completion metrics

**Display Options**:
1. Interactive flowchart (clickable graph)
2. Hierarchical tree view
3. Table with columns (Epic | Stories | Status)
4. Multiple switchable views

#### View 4: Epic/Story Detail (🔍)
**Content**:
- Complete epic or story information
- Structured sections clearly displayed
- Related QA gates and assessments
- Links to source documents

**Display**:
- Clean, readable markdown rendering
- Mermaid diagram rendering
- Table of contents for navigation
- Inter-document links support

### F5: Markdown Rendering & Navigation
**Description**: Beautiful, functional markdown visualization

**Features**:
- Clean, pleasant markdown rendering
- Automatic table of contents generation
- Inter-document navigation (clickable links)
- Mermaid diagram rendering
- Code syntax highlighting
- Responsive design

---

## 5. Data Requirements

### Data Sources
| Data Type | Source | Criticality | Description |
|-----------|--------|-------------|-------------|
| Project metadata | User input | Low | Project name, GitHub URL |
| Documentation files | Public GitHub repos | Low | Markdown files, structure |
| Extracted content | LLM processing | Low | Structured information from docs |
| User accounts | Internal DB | Low | Email, password hash, role |
| Sync metadata | System | Low | Timestamps, commit hashes |

### Data Criticality Assessment

**Personal Data**: ❌ None (GDPR compliant)
- Only user email/password for internal authentication
- No client or employee personal information

**Sensitive Data (OIV)**: ❌ None
- Public GitHub repositories only
- No sensitive business information

**Confidential Data**: ❌ None for POC
- Public repositories with technical documentation
- No access control requirements at document level in POC

**Future Industrialization Consideration**:
- Private repositories support will require GitHub OAuth
- User role-based access control (PM, PO, Dev, QA)
- Project-level access permissions

---

## 6. Expected Benefits

### Qualitative Benefits

#### Improved User Experience
- **Current**: Navigating GitHub markdown files is tedious and unintuitive
- **Future**: Pleasant, structured, and visual documentation exploration
- **Impact**: Higher documentation adoption and usage

#### Enhanced Project Visibility
- **Current**: Impossible to get project status overview from scattered files
- **Future**: Clear dashboard with status indicators and progress metrics
- **Impact**: Better project tracking and stakeholder communication

#### Faster Onboarding
- **Current**: New team members struggle to understand project structure
- **Future**: Guided navigation through documentation phases
- **Impact**: Reduced onboarding time for new developers/POs

#### Better Collaboration
- **Current**: Difficult to discuss specific epics/stories without context
- **Future**: Shareable views with clear structure and relationships
- **Impact**: More efficient team meetings and alignment

#### Visual Insights
- **Current**: No way to visualize epic-story dependencies
- **Future**: Interactive graph showing project structure
- **Impact**: Better planning and dependency management

### Quantitative Benefits (Estimated)

#### Time Savings
- **Documentation Search**: -40% time spent finding information
  - Before: ~15 min to locate specific story in GitHub
  - After: ~5 min with search and structured navigation
  - For team of 10 PO/PM checking docs daily: **~70 hours/month saved**

#### Meeting Efficiency
- **Status Review Meetings**: -30% meeting time
  - Before: 60 min meetings to review project status manually
  - After: 40 min with pre-generated dashboard views
  - For 2 meetings/week: **~3 hours/week saved per project**

#### Onboarding Speed
- **New Team Member Ramp-up**: -50% onboarding time
  - Before: 2 days to understand project structure
  - After: 1 day with guided documentation
  - For 5 new members/quarter: **5 days saved per quarter**

#### Error Reduction
- **Misunderstanding/Rework**: -20% errors due to incomplete info
  - Clearer acceptance criteria and status visibility
  - Better QA gate tracking
  - Estimated **2-3% productivity gain** on development

### ROI Estimate (First Year Post-Industrialization)

**Costs**:
- POC Development: 4-6 weeks (1 developer) ~ €15-20K
- Industrialization: 8-12 weeks (1-2 developers) ~ €40-60K
- Infrastructure (Cloud): €2-3K/year
- Maintenance: €10K/year
- **Total First Year**: €67-93K

**Benefits** (for 10 projects, 20 active users):
- Time savings: ~840 hours/year = €40K
- Meeting efficiency: ~150 hours/year = €15K
- Reduced rework: ~3% on development effort = €30K
- **Total First Year**: €85K

**Simple ROI**: Positive from Year 1 (~€0-20K gain)  
**Break-even**: Within 12-18 months  
**Long-term Value**: Scales with project count and team size

---

## 7. Solution Orientation

### Security: Open
**Rationale**: 
- POC uses only public GitHub repositories
- No sensitive or OIV data involved
- No data leaves the company (self-hosted)
- Internal cloud infrastructure

**Future Consideration**:
- If private repositories with sensitive architecture → may require Trust approach
- Current scope: Open approach is sufficient

### Solution Type: Specific Solution (with Agentic components)

**Classification**: Custom Application with AI Capabilities

**Rationale**:
- **Not a pure RAG solution**: Goes beyond simple document Q&A
- **Not purely Agentic**: Not a conversational multi-turn chatbot
- **Specific Application** because:
  - Custom UI/UX tailored to BMAD Method structure
  - Integration with GitHub API
  - Database persistence (pgvector, Neo4j)
  - Multi-view dashboard
  - Structured data extraction and visualization
  - Graph rendering of relationships

**AI/Agentic Components**:
- LLM-powered content extraction and structuring
- Semantic understanding of BMAD patterns
- Intelligent parsing with format variation tolerance
- Could add: semantic search, document summarization, chatbot assistant (future)

---

## 8. Technical Architecture (High-Level)

### Technology Stack

**Frontend**:
- Framework: React with TypeScript
- UI Components: shadcn/ui
- Styling: Tailwind CSS
- Graph Visualization: D3.js or React Flow
- Markdown Rendering: react-markdown
- Mermaid: mermaid.js

**Backend**:
- Framework: Python FastAPI
- Async processing: Celery (for GitHub sync)
- API: RESTful endpoints

**Agentic / AI Layer**:
- Framework: Pydantic AI
- LLM Provider: OLLAMA (local/self-hosted)
- Embeddings: sentence-transformers (for future semantic search)

**Databases**:
- **pgvector** (PostgreSQL with vector extension)
  - Store document content and embeddings
  - Relational data (projects, users, metadata)
  - Enable semantic search capabilities
- **Neo4j** (Graph Database)
  - Store epic → story relationships
  - Enable graph queries and visualization
  - Handle BMAD structure dependencies

**Infrastructure**:
- Containerization: Docker & Docker Compose
- Orchestration: Kubernetes (for industrialization)
- CI/CD: GitLab CI or GitHub Actions
- Hosting: Internal cloud infrastructure

**External Integrations**:
- GitHub API (read-only for public repos)
- Future: GitHub OAuth (for private repos)

### Architecture Pattern
- Clean Architecture / Hexagonal Architecture
- API-first design
- Event-driven for synchronization (future: webhooks)
- Microservices-ready (separation of concerns)

---

## 9. POC Scope & Success Criteria

### POC Scope

**Duration**: 4-6 weeks (rapid but structured POC)

**Development Method**: Claude Code + BMAD Method
- Self-referential: BMADFlow will visualize its own documentation
- Dogfooding approach for immediate feedback

**Pilot Projects**: 2-3 projects
1. **AgentLab** (primary validation project)
2. **BMADFlow** (self-documentation)
3. One additional BMAD project (TBD)

**Core Features for POC**:
- ✅ Project addition (GitHub URL input)
- ✅ Manual GitHub synchronization
- ✅ Intelligent content extraction (LLM-based)
- ✅ Project dashboard with 4 views (Scoping, Architecture, Epics, Detail)
- ✅ Beautiful markdown rendering with Mermaid
- ✅ Epic → Story graph visualization (at least one view type)
- ✅ Status detection (draft/dev/done)

**Out of Scope for POC**:
- ❌ Authentication (simple or none for POC)
- ❌ Multi-user management
- ❌ Real-time synchronization
- ❌ Semantic search / Chatbot
- ❌ Private repositories
- ❌ Performance optimization at scale
- ❌ Advanced analytics / metrics

### Success Criteria (To Be Determined During POC)

**Primary Objective**: Validate UI/UX and functionality value

**Testing Approach**:
- Use POC with pilot projects
- Collect feedback from PO/PM users
- Assess UX compared to GitHub navigation
- Evaluate graph visualization utility

**Key Validation Points**:
1. ✅ Intelligent extraction works on 2-3 pilot projects
2. ✅ Dashboard provides superior UX vs GitHub
3. ✅ Epic → Story graph is exploitable and valuable
4. ✅ Positive user feedback (PO/PM testers)
5. ✅ Mermaid diagrams render correctly
6. ✅ Navigation and document linking work smoothly
7. ✅ Synchronization performance is acceptable (< 5 min for typical project)

**Decision Criteria for Industrialization**:
- User satisfaction threshold (e.g., 80% positive feedback)
- Technical feasibility confirmed
- Clear value demonstration vs current GitHub navigation
- Roadmap for industrialization features validated

---

## 10. Industrialization Considerations

### Target Scale (Post-POC)
- **Projects**: ~10 active projects
- **Users**: 20-30 concurrent users (PM, PO, Dev, QA)
- **Repositories**: Public GitHub only initially

### Features to Add for Production

**Authentication & Authorization**:
- Simple user management: email/password
- User roles: PM, PO, Dev, QA
- Project-level access control (future enhancement)

**Infrastructure**:
- Internal cloud hosting
- Kubernetes deployment
- High availability setup
- Backup and disaster recovery

**Advanced Features** (Post-Industrialization):
- Private repository support (GitHub OAuth)
- Automated synchronization (webhooks or scheduled)
- Semantic search across projects
- AI assistant chatbot for documentation Q&A
- Export capabilities (PDF, JSON)
- Notification system (project updates)
- Analytics dashboard (usage, popular docs)
- Multi-project overview
- Team collaboration features (comments, annotations)

**Performance & Scalability**:
- Caching strategies
- Optimized database queries
- Lazy loading for large documents
- Background job processing
- Rate limiting and throttling

**Monitoring & Observability**:
- Application performance monitoring
- User activity tracking
- Error logging and alerting
- Usage analytics

---

## 11. Complexity Assessment

### Overall Complexity: **MEDIUM**

#### Simple Components ✅
- Frontend dashboard UI with shadcn (well-defined components)
- Markdown rendering (established libraries)
- GitHub API integration (read-only, public repos)
- Basic project CRUD operations

#### Medium Complexity Components ⚠️
- **Intelligent content extraction with LLM**
  - Need to handle format variations
  - Parsing and structuring markdown
  - LLM prompt engineering for consistent extraction
  - Risk: Accuracy depends on OLLAMA model quality
  
- **Graph visualization (Epics → Stories)**
  - Relationship extraction from documents
  - Graph database (Neo4j) setup and queries
  - Interactive visualization rendering
  
- **Dual database architecture**
  - pgvector + Neo4j integration
  - Data synchronization between databases
  - Query optimization across both systems

- **BMAD structure parsing**
  - Understanding sharded documents (PRD, Architecture)
  - Handling index.md files
  - Cross-document link resolution

#### Complex Components (Lower Risk for POC) 🔸
- **Status detection logic**: Can be simplified for POC (explicit > inferred)
- **Performance at scale**: Not critical for 2-3 projects POC
- **Multi-view synchronization**: Can be basic for POC

### Risk Factors

**Technical Risks**:
- **LLM extraction accuracy** (Medium Risk)
  - Mitigation: Start with rule-based + LLM hybrid
  - Fallback: Display raw content if extraction fails
  
- **Neo4j learning curve** (Low-Medium Risk)
  - Mitigation: Graph queries are well-documented
  - Alternative: Start with relational DB for relationships if needed

- **Mermaid rendering complexity** (Low Risk)
  - Well-established library (mermaid.js)
  - Fallback: Display as code block

**Organizational Risks**:
- **BMAD documentation consistency** (Medium Risk)
  - Projects may have variations in structure
  - Mitigation: Test on multiple projects, handle gracefully
  
- **User adoption** (Low Risk)
  - Clear improvement over GitHub navigation
  - Dogfooding approach ensures immediate feedback

### Effort Estimation

**POC Development** (1 developer with Claude Code):
- Week 1-2: Backend foundation (FastAPI, DB setup, GitHub sync)
- Week 3-4: Frontend dashboard (React, shadcn, views)
- Week 5: LLM extraction + graph visualization
- Week 6: Integration, testing, refinement
- **Total: 4-6 weeks**

**Industrialization** (1-2 developers):
- Architecture hardening: 2 weeks
- Authentication/authorization: 2 weeks
- Private repo support: 2 weeks
- Performance optimization: 2 weeks
- Monitoring/observability: 1 week
- Production deployment: 1 week
- Testing and QA: 2 weeks
- **Total: 8-12 weeks**

---

## 12. Recommendations

### ✅ GO FOR POC

**Strong Rationale**:
1. **Clear user pain point**: GitHub navigation is universally acknowledged as suboptimal
2. **Well-defined scope**: POC is focused and achievable in 4-6 weeks
3. **Low risk**: Public repos, no sensitive data, established tech stack
4. **Immediate value**: Even basic improvements over GitHub would be valuable
5. **Self-referential validation**: Using BMADFlow to document itself provides instant feedback
6. **Positive ROI**: Benefits outweigh costs from Year 1

### 🎯 POC Priorities (MVP Features)

**Must Have (P0)**:
1. Project addition + GitHub sync (manual)
2. Dashboard with Scoping + Epics views
3. Basic markdown rendering with Mermaid
4. Simple epic/story list view (can defer complex graph)
5. LLM-based content extraction (at least for user stories)

**Should Have (P1)**:
1. Architecture view
2. Interactive graph visualization
3. Epic/Story detail view
4. Status detection (explicit status first)

**Could Have (P2)**:
1. Advanced graph interactions
2. Semantic search
3. Multiple visualization options

### 📋 Pre-POC Actions

**Before Starting Development**:
1. ✅ Select 2-3 pilot projects (AgentLab + BMADFlow + 1 more)
2. ✅ Review BMAD documentation structure consistency
3. ✅ Identify 5-8 test users (PO/PM) for feedback
4. ✅ Set up development environment (OLLAMA, Docker)
5. ✅ Define clear feedback collection process

**During POC**:
1. Weekly demos to stakeholders
2. Continuous user feedback collection
3. Track time spent on each component (for industrialization estimate)
4. Document technical decisions and learnings
5. Maintain clear backlog for industrialization phase

### 🚀 Industrialization Decision Gate

**After POC, evaluate**:
- User feedback score (target: >80% positive)
- Feature completeness vs expectations
- Technical debt assessment
- Industrialization effort estimate
- Budget approval
- Resource allocation (1-2 developers for 8-12 weeks)

**Go/No-Go Decision Factors**:
- ✅ GO if: Clear value demonstrated, positive feedback, technical feasibility confirmed
- ⚠️ PIVOT if: UX needs major rework, feature prioritization needs adjustment
- ❌ NO-GO if: No clear value over GitHub, technical blockers, insufficient user interest

---

## 13. Appendix

### Reference Documentation
- **BMAD Core Documentation**: https://github.com/bmad-code-org/BMAD-METHOD/blob/main/docs
- **Example Project (AgentLab)**: https://github.com/twattier/agent-lab/tree/main/docs

### Key Technologies Documentation
- **shadcn/ui**: https://ui.shadcn.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic AI**: https://ai.pydantic.dev/
- **pgvector**: https://github.com/pgvector/pgvector
- **Neo4j**: https://neo4j.com/docs/
- **OLLAMA**: https://ollama.ai/

### Project Contacts
- **Business Owner**: Thierry W (DSI - Operational Performance Team)
- **Development**: Claude Code + BMAD Method (self-documenting)
- **Users**: PM, PO, Dev, QA teams

---

**Document Version**: 1.0  
**Date**: October 1, 2025  
**Status**: Ready for POC Kick-off  
**Next Steps**: POC Development (4-6 weeks) → User Testing → Industrialization Decision