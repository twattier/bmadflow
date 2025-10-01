# Epic 3: Multi-View Documentation Dashboard

**Status:** Draft

## Epic Goal

Create 4-view dashboard (Scoping, Architecture, Epics, Detail) with beautiful markdown rendering, Mermaid diagrams, and navigation. Deliver core "better than GitHub" UX value proposition.

## Epic Description

This epic delivers the core user experience value of BMADFlow: making documentation exploration significantly better than GitHub's file navigation. By the end of this epic, users can browse documentation through 4 purpose-built views (Scoping, Architecture, Epics, Detail), read beautifully rendered markdown with syntax-highlighted code blocks and Mermaid diagrams, navigate between documents via clickable inter-document links, and see real-time sync status.

The epic includes critical UX features like auto-generated table of contents with smooth scrolling (Story 3.3), Mermaid diagram rendering with graceful fallback (Story 3.5), and persistent sync status indicators (Story 3.8).

**Critical Path:** Scoping + Detail views working by end of Week 3; Architecture view and Mermaid complete in Week 4.

## Stories

### Story 3.1: Scoping View - Document Cards Grid

As a **user**,
I want **Scoping view to display grid of scoping documents as cards**,
so that **I can quickly see all research, PRD, and use case documents**.

**Acceptance Criteria:**

1. Scoping view fetches documents where doc_type = 'scoping' from `/api/projects/{id}/documents?type=scoping` endpoint
2. Documents displayed as card grid (3 columns on desktop per UX spec)
3. Each card shows: document title (extracted from first H1 heading), excerpt (first 150 characters of content), last modified date, status badge if available
4. Cards are clickable - clicking navigates to Detail view with document_id parameter
5. Cards show visual loading state (skeleton placeholders) while data fetches
6. Empty state displayed if no scoping documents found: "No scoping documents found. Check repository structure."
7. Search/filter input at top of grid (filters document titles as user types - simple client-side filtering for POC)

### Story 3.2: Detail View - Markdown Rendering

As a **user**,
I want **Detail view to render markdown content beautifully**,
so that **reading documentation in BMADFlow is significantly better than GitHub**.

**Acceptance Criteria:**

1. Detail view fetches single document content from `/api/documents/{id}` endpoint
2. Markdown rendered using react-markdown library with remark plugins (GitHub Flavored Markdown support)
3. Rendered content includes: headers (h1-h6), paragraphs, lists (ordered/unordered), tables, blockquotes, inline code, code blocks, links, images
4. Code blocks have syntax highlighting using Prism.js or similar (supports TypeScript, Python, JavaScript, YAML, JSON)
5. Each code block includes "Copy" button in top-right corner
6. Content area has max-width constraint (1280px per UX spec) for readability
7. Typography uses Inter font with 1.5 line height for body text

### Story 3.3: Detail View - Table of Contents

As a **user**,
I want **Table of Contents sidebar in Detail view**,
so that **I can quickly jump to specific sections in long documents**.

**Acceptance Criteria:**

1. TOC automatically generated from document headings (H2 and H3 levels included)
2. TOC displayed in left sidebar (256px width per UX spec, collapsible on narrow screens)
3. TOC items clickable - clicking scrolls to corresponding section with smooth animation (400ms per UX spec)
4. Active section highlighted in TOC based on scroll position (heading currently visible at top of viewport)
5. TOC shows hierarchical structure (H2 as parent, H3 nested with indentation)
6. TOC sticky positioned (stays visible while scrolling main content)
7. Empty state: TOC hidden if document has <3 headings

### Story 3.4: Architecture View - Tech Stack Display

As a **user**,
I want **Architecture view to display tech stack and system design documents**,
so that **I can understand technical decisions and architecture**.

**Acceptance Criteria:**

1. Architecture view fetches documents where doc_type = 'architecture'
2. View prioritizes displaying "tech-stack.md" prominently if it exists (top section)
3. Markdown tables in architecture docs rendered correctly (tech stack typically documented as table)
4. Document cards similar to Scoping view but with architecture-specific icons (🏗️)
5. If "architecture.md" exists, display as featured card (larger, full-width) before other architecture docs

### Story 3.5: Mermaid Diagram Rendering

As a **user**,
I want **Mermaid diagrams to render as visual diagrams instead of code blocks**,
so that **I can understand system architecture visually**.

**Acceptance Criteria:**

1. Markdown rendering (from Story 3.2) detects code blocks with language = `mermaid`
2. Mermaid.js library integrated to render diagrams client-side
3. Supported diagram types: flowchart, sequence diagram, class diagram, ER diagram, C4 diagram
4. Diagrams rendered with default Mermaid theme (light mode per UX spec)
5. **Graceful fallback:** If Mermaid rendering fails (invalid syntax, unsupported diagram type), display original code block with warning message: "⚠️ Diagram could not be rendered. Showing code instead."
6. **Timebox: 1.5 days max** - If basic integration works in 1 day, spend 0.5 day on error handling. If complex (2+ days), implement fallback only and defer full rendering

### Story 3.6: Epics View - List Display

As a **user**,
I want **Epics view to show list of all epics with status indicators**,
so that **I can see project epic structure at a glance**.

**Acceptance Criteria:**

1. Epics view fetches documents where doc_type = 'epic' from API
2. Epics displayed as list (table or card list) with columns: Epic Title, Status, Story Count, Last Modified
3. Status displayed with color-coded badge: Draft (gray), Dev (blue), Done (green) per UX spec
4. Story Count calculated from relationships table (count child documents where relationship_type = 'contains')
5. Clicking epic row navigates to Detail view showing full epic content
6. Epics sorted by filename/number (e.g., Epic 1, Epic 2, Epic 3) for logical sequence
7. Status rollup widget displayed at top: "X epics total | Y draft, Z in dev, W done"

### Story 3.7: Inter-Document Link Navigation

As a **user**,
I want **markdown links to other documents to navigate within BMADFlow**,
so that **I can explore related documentation without leaving the dashboard**.

**Acceptance Criteria:**

1. Markdown rendering (Story 3.2) detects links to `.md` files (e.g., `[Architecture](../architecture.md)`)
2. Link resolver service maps file paths to document IDs in database
3. Links rewritten to navigate to Detail view route: `/detail/{document_id}` using React Router Link component
4. Clicking inter-document link navigates within SPA (no page reload)
5. Breadcrumb navigation updated to show: Project > Current View > Document Title
6. External links (http/https) open in new tab with `target="_blank" rel="noopener"`
7. Broken links (reference non-existent document) styled differently (red text) with tooltip: "Document not found"

### Story 3.8: Sync Status Indicator

As a **user**,
I want **persistent sync status indicator in dashboard header**,
so that **I always know if my documentation is up-to-date**.

**Acceptance Criteria:**

1. Header displays last sync timestamp (e.g., "Last synced: 2 hours ago")
2. "Sync Now" button in header triggers manual sync
3. Button disabled during active sync with loading spinner
4. Sync progress displayed as toast notification in top-right (per UX spec): "Syncing... 45 of 100 documents"
5. Toast notification updates every 2 seconds via polling sync-status endpoint
6. On sync complete, toast shows success message: "✓ Sync complete. Extracted 95 of 100 documents." (auto-dismisses after 4 seconds)
7. On sync failure, toast shows error with "Retry" action
8. Dashboard content auto-refreshes after successful sync (React Query cache invalidation)

## Dependencies

- Epic 1 Stories 1.5-1.6: Dashboard shell and navigation functional
- Epic 2 Story 2.5: Extraction pipeline provides structured data for views
- shadcn/ui components, react-markdown, Mermaid.js libraries

## Success Metrics

- All 4 views (Scoping, Architecture, Epics, Detail) functional and navigable
- Markdown rendering quality rated 4-5 stars by pilot users
- Mermaid diagrams render successfully or show graceful fallback
- Inter-document navigation works seamlessly
- Users report 80%+ time reduction vs GitHub navigation

## Timeline

**Target:** Week 3-4 of POC
- **Week 3 (Must-Have):** Stories 3.1, 3.2, 3.3 (Scoping + Detail views)
- **Week 4 (Should-Have):** Stories 3.4, 3.5, 3.6, 3.7, 3.8

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Epic extracted from PRD v1.0 | Sarah (PO) |
