# BMADFlow Documentation

Welcome to the BMADFlow project documentation. This is a comprehensive documentation hub for the intelligent documentation visualization platform.

## 📋 Project Overview

BMADFlow transforms scattered GitHub markdown files into interactive, methodology-aware project dashboards using AI-powered content extraction (OLLAMA), epic-to-story graph visualization, and purpose-built multi-view dashboards.

**Goal:** Enable teams to find information 80% faster while providing stakeholders with instant project status visibility.

---

## 📚 Core Documentation

### Product Requirements

**[Product Requirements Document (PRD)](prd.md)** | [Sharded PRD](prd/)

Complete product requirements including functional requirements, user interface goals, technical assumptions, and epic definitions.

- [Goals and Background Context](prd/goals-and-background-context.md)
- [Requirements (FR/NFR)](prd/requirements.md)
- [User Interface Design Goals](prd/user-interface-design-goals.md)
- [Technical Assumptions](prd/technical-assumptions.md)
- [Epic List](prd/epic-list.md)
- [Next Steps](prd/next-steps.md)

**Version:** 1.1 (Sharded) | **Status:** ✅ Ready for Development

### Architecture

**[Fullstack Architecture Document](architecture.md)** | [Sharded Architecture](architecture/)

Complete technical architecture including frontend, backend, data models, API specifications, and deployment strategy.

**Key Sections:**
- [High Level Architecture](architecture/high-level-architecture.md)
- [Tech Stack](architecture/tech-stack.md)
- [Data Models](architecture/data-models.md)
- [API Specification](architecture/api-specification.md)
- [Frontend Architecture](architecture/frontend-architecture.md)
- [Backend Architecture](architecture/backend-architecture.md)
- [Database Schema](architecture/database-schema.md)
- [Coding Standards](architecture/coding-standards.md)
- [Development Workflow](architecture/development-workflow.md)
- [Deployment Architecture](architecture/deployment-architecture.md)

**Version:** 1.1 (Sharded) | **Status:** ✅ Ready for Development

### User Experience

**[Front-End Specification](front-end-spec.md)**

Detailed UI/UX requirements, component specifications, and design system guidelines.

---

## 📊 Epics & Stories

### Epic Files

All epics with complete descriptions, goals, stories, and acceptance criteria:

1. **[Epic 1: Foundation, GitHub Integration & Dashboard Shell](epics/epic-1-foundation-github-dashboard.md)** (8 stories)
   - Establish core infrastructure, Docker setup, GitHub API integration, dashboard shell

2. **[Epic 2: LLM-Powered Content Extraction](epics/epic-2-llm-content-extraction.md)** (9 stories)
   - OLLAMA integration, user story extraction, epic extraction, status detection

3. **[Epic 3: Multi-View Documentation Dashboard](epics/epic-3-multi-view-dashboard.md)** (8 stories)
   - Scoping view, Architecture view, Epics view, Detail view with markdown rendering

4. **[Epic 4: Epic-Story Relationship Visualization](epics/epic-4-epic-story-visualization.md)** (8 stories)
   - Epic-story table view, graph visualization, search/filter, error handling

**Total:** 4 Epics | 33 Stories

### Story Files

All 33 user stories with acceptance criteria and dependencies in [stories/](stories/) folder:

- **Epic 1:** [Story 1.1](stories/story-1-1-project-infrastructure-setup.md) through [Story 1.8](stories/story-1-8-ci-cd-pipeline-setup.md)
- **Epic 2:** [Story 2.1](stories/story-2-1-ollama-integration-and-model-setup.md) through [Story 2.7c](stories/story-2-7c-acceptance-criteria-parsing.md)
- **Epic 3:** [Story 3.1](stories/story-3-1-scoping-view-document-cards-grid.md) through [Story 3.8](stories/story-3-8-sync-status-indicator.md)
- **Epic 4:** [Story 4.1](stories/story-4-1-epic-story-relationship-data-api.md) through [Story 4.7](stories/story-4-7-pilot-user-feedback-collection-and-documentation.md)

---

## 🔍 Qualification Documents

Pre-project research and analysis documents:

- [Initial Project Brief](qualification/INITIAL.md)
- [Project Brief](qualification/brief.md)
- [Competitor Analysis](qualification/competitor-analysis.md)
- [Market Research](qualification/market-research.md)

---

## 🎯 Quick Start for Developers

### Next Step: Begin Development

**Start here:** [Story 1.1: Project Infrastructure Setup](stories/story-1-1-project-infrastructure-setup.md)

**Developer Resources:**
- [Unified Project Structure](architecture/unified-project-structure.md) - Monorepo layout
- [Development Workflow](architecture/development-workflow.md) - Setup and commands
- [Coding Standards](architecture/coding-standards.md) - Code style and conventions
- [Tech Stack](architecture/tech-stack.md) - Technologies and versions

### POC Timeline

- **Week 0:** Architecture review (complete)
- **Week 1:** Epic 1 - Foundation & GitHub Integration (8 stories)
- **Week 2:** Epic 2 - LLM Content Extraction (9 stories)
- **Week 3-4:** Epic 3 - Multi-View Dashboard (8 stories)
- **Week 5-6:** Epic 4 - Visualization & Polish (8 stories)

---

## 📈 Project Status

| Component | Status | Version | Notes |
|-----------|--------|---------|-------|
| PRD | ✅ Complete | v1.1 | Sharded, epics/stories extracted |
| Architecture | ✅ Complete | v1.1 | Sharded, ready for development |
| Epics | ✅ Complete | 1.0 | 4 epic files in [epics/](epics/) |
| Stories | ✅ Complete | 1.0 | 33 story files in [stories/](stories/) |
| Development | 🚀 Ready | - | Start with Story 1.1 |

---

## 🔗 Related Resources

- **Configuration:** [.bmad-core/core-config.yaml](../.bmad-core/core-config.yaml)
- **GitHub Repository:** Project files tracked in Git
- **BMAD Methodology:** Structured development approach with epics, stories, and acceptance criteria

---

**Last Updated:** 2025-10-01
**Project Owner:** Product Owner (Sarah)
**Architecture Owner:** Architect (Winston)
**Development Team:** Ready to begin Epic 1
