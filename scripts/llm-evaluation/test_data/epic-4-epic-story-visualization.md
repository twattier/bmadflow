# Epic 4: Epic-Story Relationship Visualization

**Status:** Draft

## Epic Goal

Build table/list visualization of epic-to-story relationships with status color-coding and click-to-navigate, enabling users to understand project structure at a glance. Interactive graph with zoom/pan as stretch goal if Week 5 timeline permits (Week 6 = polish, pilot testing, bug fixes).

## Epic Description

This epic delivers the final core feature of BMADFlow: visualizing epic-to-story relationships to provide instant project structure understanding. By the end of this epic, users can view all epics and their related stories in a hierarchical table/list view with color-coded status indicators, search/filter across all content, and see status rollup widgets showing project health at a glance.

The epic includes comprehensive error handling (Story 4.6) and pilot user feedback collection (Story 4.7) to measure POC success. An interactive graph visualization (Stories 4.3a-b) is a stretch goal, with the table view providing full functionality as the must-have baseline.

## Stories

### Story 4.1: Epic-Story Relationship Data API

As a **frontend developer**,
I want **API endpoint returning epic-story relationship graph data**,
so that **I can build visualization components**.

**Acceptance Criteria:**

1. GET `/api/projects/{id}/relationships` endpoint returns JSON representing epic-story graph
2. Response format: `{ nodes: [ {id, title, type: 'epic'|'story', status, document_id} ], edges: [ {source_id, target_id, type: 'contains'} ] }`
3. Nodes include extracted epic/story data (title from extracted_epics/extracted_stories, status for color-coding)
4. Edges derived from relationships table (epic → stories links)
5. Endpoint includes optional query param `?epic_id=` to filter graph to single epic and its stories
6. Response cached with 5-minute TTL (Redis cache)

### Story 4.2: Epic-Story Table View

As a **user**,
I want **table view showing epics and their related stories**,
so that **I can understand project structure without needing graph visualization**.

**Acceptance Criteria:**

1. Epics view includes toggle button: "Graph View" | "Table View" (Table is default for POC)
2. Table view displays hierarchical list: Epic row (bold, status badge) followed by indented Story rows
3. Table columns: Title, Status, Type (Epic/Story), Last Modified
4. Epic rows expandable/collapsible (clicking epic toggles visibility of child stories)
5. All epics expanded by default on initial load
6. Status displayed with color-coded badge (draft=gray, dev=blue, done=green)
7. Clicking any row (epic or story) navigates to Detail view for that document

### Story 4.3a: Basic Graph Visualization (MVP)

As a **user**,
I want **interactive graph visualization of epic-story relationships**,
so that **I can visually explore project structures**.

**Acceptance Criteria:**

1. React Flow library integrated into Epics view
2. Graph renders nodes (epics + stories) and edges (contains relationships)
3. Nodes color-coded by status: Draft (gray), Dev (blue), Done (green)
4. Hierarchical layout (epics at top, stories below)
5. Clicking node navigates to Detail view for that document
6. Basic zoom/pan with mouse wheel and drag
7. Handles 50 nodes without performance issues

**Stretch Goal - Ship only if Week 5 timeline permits (2 days):**

### Story 4.3b: Graph Polish and Advanced Features (Stretch)

As a **user**,
I want **polished graph visualization with advanced interactions**,
so that **exploring complex relationships is effortless**.

**Acceptance Criteria:**

1. Minimap in bottom-right corner
2. "Center View" reset button
3. Node labels with smart truncation
4. Force-directed layout option (user toggle)
5. Hover tooltips showing full title
6. Smooth animations and transitions

### Story 4.4: Status Rollup Widget

As a **user**,
I want **status summary widget in Epics view**,
so that **I can see project health at a glance**.

**Acceptance Criteria:**

1. Widget displayed prominently in Epics view (top-right sidebar per UX spec)
2. Widget shows: "X epics | Y stories"
3. Widget shows status breakdown: "Z draft, W in dev, V done"
4. Status counts derived from extracted_epics and extracted_stories tables
5. Widget shows percentage complete: "(V/Y stories done = X%)"
6. Visual progress bar shows completion percentage (green fill)

### Story 4.5: Search/Filter Across Epics and Stories

As a **user**,
I want **search functionality to find specific epics or stories by keyword**,
so that **I can quickly locate information without browsing entire graph**.

**Acceptance Criteria:**

1. Search input field at top of Epics view (consistent with Scoping view from Story 3.1)
2. Search filters both epics and stories by title match (case-insensitive substring search)
3. Table view: Filtered results show matching epics/stories, other rows hidden
4. Graph view: Filtered results highlight matching nodes (dimmed/grayed out non-matches)
5. Search is client-side for POC (filters already-loaded data, no server query)
6. Clear button (X icon) in search input resets filter
7. Debounced input (300ms delay) to avoid re-filtering on every keystroke

### Story 4.6: Error Handling and Resilience

As a **user**,
I want **graceful error handling throughout the dashboard**,
so that **temporary failures don't break my workflow**.

**Acceptance Criteria:**

1. All API calls wrapped in try/catch with user-friendly error messages
2. Network errors show toast notification: "⚠️ Connection lost. Retrying..." with auto-retry (exponential backoff, max 3 attempts)
3. GitHub sync failures display actionable errors: "GitHub rate limit exceeded. Try again in X minutes or add Personal Access Token."
4. Extraction failures (low confidence score) marked visually in Detail view: "⚠️ Some information may be inaccurate. Extracted with low confidence."
5. Missing documents (broken inter-doc links) show placeholder: "Document not found. It may have been deleted or moved."
6. Empty states throughout: No projects, no documents, no epics, no stories (with helpful next-step guidance)
7. All errors logged to Sentry (error tracking) for debugging

### Story 4.7: Pilot User Feedback Collection and Documentation

As a **pilot user**,
I want **feedback form to rate my BMADFlow experience and access to user documentation**,
so that **the PM can measure POC success and I can learn how to use the platform effectively**.

**Acceptance Criteria:**

1. Feedback button in dashboard header (icon: 💬)
2. Modal form with fields: (1) Overall rating (1-5 stars), (2) "Is BMADFlow better than GitHub?" (Yes/No), (3) Favorite feature (dropdown), (4) Improvement suggestions (textarea)
3. Form submits to `/api/feedback` endpoint, stored in database
4. Thank you message after submission: "Thank you! Your feedback helps us improve BMADFlow."
5. PM can export feedback via admin endpoint: GET `/api/admin/feedback?project_id=` (CSV export)
6. Feedback form accessible from all views (persistent header button)
7. Help button (icon: ❓) in dashboard header opens user documentation modal or sidebar
8. User documentation includes: (a) Quick start guide with screenshots, (b) How to sync repositories, (c) How to navigate the 4 views, (d) How to interpret status colors, (e) FAQ section
9. Documentation written in markdown, rendered using existing MarkdownRenderer component
10. Documentation stored in `/docs/user-guide.md` file, loaded dynamically by frontend

## Dependencies

- Epic 2 Story 2.5: Extraction pipeline provides relationship data
- Epic 3 Stories 3.2, 3.6: Detail view and Epics view functional
- React Flow library (for graph visualization stretch goal)
- Sentry SDK for error tracking

## Success Metrics

- Table view functional and usable for 50+ node projects
- Search/filter works across all epics and stories
- 70%+ pilot users find relationship visualization valuable
- All critical errors handled gracefully with user guidance
- Feedback collection yields 80%+ positive ratings

## Timeline

**Target:** Week 5-6 of POC
- **Week 5 (Must-Have):** Stories 4.1, 4.2, 4.4, 4.5, 4.6
- **Week 6 (Nice-to-Have):** Story 4.3a-b (graph visualization), Story 4.7, polish

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Epic extracted from PRD v1.0 | Sarah (PO) |
