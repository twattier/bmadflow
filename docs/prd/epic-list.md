# Epic List

The BMADFlow project consists of 4 epics with 33 total user stories. Full epic details with all story acceptance criteria are in dedicated epic files.

## Epic 1: Foundation, GitHub Integration & Dashboard Shell (8 stories)

**Goal:** Establish core infrastructure (Docker, Postgres, FastAPI, React + Vite + shadcn/ui) and deliver working dashboard shell with 4-view tab navigation. Backend can fetch and store raw GitHub markdown files. First deployable increment shows UI architecture and "look and feel."

**Full Details:** [Epic 1: Foundation, GitHub Integration & Dashboard Shell](../epics/epic-1-foundation-github-dashboard.md)

## Epic 2: LLM-Powered Content Extraction (9 stories)

**Goal:** Implement OLLAMA-based extraction of structured information from BMAD markdown (user stories, epics, status, relationships). Developer validates extraction logic on 20 sample documents in Week 2. PM/pilot users perform comprehensive 100-document accuracy validation in parallel with Epic 3 (async validation, results inform Epic 3 refinements).

**Full Details:** [Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)

## Epic 3: Multi-View Documentation Dashboard (8 stories)

**Goal:** Create 4-view dashboard (Scoping, Architecture, Epics, Detail) with beautiful markdown rendering, Mermaid diagrams, and navigation. Deliver core "better than GitHub" UX value proposition.

**Critical Path Milestones:**
- **End of Week 3 (Must-Have):** Scoping view with document cards, Detail view with basic markdown rendering
- **End of Week 4 (Should-Have):** Architecture view, Mermaid diagram support, TOC navigation
- **End of Week 4 (Nice-to-Have):** Advanced formatting, inter-document link resolution

**Full Details:** [Epic 3: Multi-View Documentation Dashboard](../epics/epic-3-multi-view-dashboard.md)

## Epic 4: Epic-Story Relationship Visualization (8 stories)

**Goal:** Build table/list visualization of epic-to-story relationships with status color-coding and click-to-navigate, enabling users to understand project structure at a glance. Interactive graph with zoom/pan as stretch goal if Week 5 timeline permits (Week 6 = polish, pilot testing, bug fixes).

**Full Details:** [Epic 4: Epic-Story Relationship Visualization](../epics/epic-4-epic-story-visualization.md)

---

**Related:**
- [Epic and Story Files](./epic-and-story-files.md) - Complete listing of all extracted files
- [Epic files directory](../epics/) - All epic files
- [Story files directory](../stories/) - All 33 story files
