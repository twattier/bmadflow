# Epic 3: Documentation Explorer & Viewer

## Epic Goal

Provide a visual file tree interface for browsing synced documentation with intelligent content rendering based on file type (markdown with TOC, CSV tables, syntax highlighting, Mermaid diagrams, and cross-document navigation).

## Pre-Development Checklist

**Complete these tasks before starting Story 3.1:**

### Critical Dependencies
- [ ] **Install Frontend Libraries**
  ```bash
  cd frontend
  npm install react-arborist react-markdown remark-gfm rehype-raw
  npm install react-syntax-highlighter @types/react-syntax-highlighter
  npm install mermaid react-mermaid2
  npm install papaparse @types/papaparse
  ```
- [ ] **Verify Ollama Setup**
  ```bash
  ollama list | grep nomic-embed-text
  ```
  Expected: Model should be listed. If not, run: `ollama pull nomic-embed-text`

- [ ] **Review Architecture Documentation**
  - Read [docs/architecture/api-specification.md](../architecture/api-specification.md)
  - Understand existing endpoints (Projects, ProjectDocs, Documents)
  - Review database schema for Documents table

### Validation
- [ ] Review [Epic 3 Validation Report](../validation/epic-3-validation-report.md)
- [ ] Confirm Epic 2 complete (Documents table populated with file_path data)

---

## Epic Status (Updated 2025-10-09)

**STATUS:** ✅ **COMPLETE** - Ready for Epic 4 (AI Chatbot Development)

All must-have stories delivered:
- Stories 3.1-3.4, 3.6: Complete (5/5 P0 stories)
- Stories 3.5 & 3.7: Deferred to backlog (P2 nice-to-have features)

---

## Story Sequencing & Dependencies

### Critical Path (Sequential) - ✅ ALL COMPLETE
```
Story 3.1 (File Tree API) ✅ DONE (2025-10-07)
    ↓
Story 3.2 (File Tree UI) ✅ DONE (2025-10-07)
    ↓
Story 3.3 (Markdown Renderer) ✅ DONE (2025-10-08)
    ↓
Story 3.4 (Mermaid Diagrams) ✅ DONE (2025-10-09)
    ↓
Story 3.6 (Cross-Doc Navigation) ✅ DONE (2025-10-09)
```

### Deferred Stories (Backlog - Nice-to-Have)
These stories were deprioritized. AI Chatbot work takes precedence:
- **Story 3.5** (CSV Viewer) - Independent file type handler [BACKLOG]
- **Story 3.7** (YAML/JSON/TXT) - Independent file type handler [BACKLOG]

### Dependency Summary
| Story | Depends On | Status | Priority | QA Score |
|-------|------------|--------|----------|----------|
| 3.1 | Epic 2 complete | ✅ DONE | P0 | 100/100 |
| 3.2 | Story 3.1 | ✅ DONE | P0 | 95/100 |
| 3.3 | Story 3.2 | ✅ DONE | P0 | 95/100 |
| 3.4 | Story 3.3 | ✅ DONE | P0 | Pending |
| 3.6 | Story 3.4 | ✅ DONE | P0 | 95/100 |
| 3.5 | Story 3.3 | Backlog | P2 | - |
| 3.7 | Story 3.3 | Backlog | P2 | - |

**Epic 3 Complete:** ✅ All P0 stories delivered (5/5)
**Next Epic:** Epic 4 - AI Chatbot Development

---

## Stories

### Story 3.1: Build File Tree API for Document Hierarchy ✅ DONE

**Status:** Done (Completed 2025-10-07)
**Story File:** [3.1-build-file-tree-api-for-document-hierarchy.md](../stories/3.1-build-file-tree-api-for-document-hierarchy.md)
**QA Gate:** PASS (100/100) - [Gate File](../qa/gates/3.1-build-file-tree-api-for-document-hierarchy.yml)

**As a** developer,
**I want** to retrieve a hierarchical file tree structure from synced documents,
**so that** I can display it in the UI.

**Acceptance Criteria:**
1. ✅ REST API endpoint `GET /api/projects/{id}/file-tree` returns hierarchical JSON structure
2. ✅ File tree structure includes: folders (nested), files (with metadata: id, name, path, type, size)
3. ✅ Tree built from documents table file_path field, parsing directory structure
4. ✅ Files grouped by ProjectDoc if multiple ProjectDocs exist in Project
5. ✅ Tree sorted: folders first (alphabetical), then files (alphabetical)
6. ✅ Unit tests for tree-building logic (5 tests passing)
7. ✅ Integration test: sync repo with nested folders, verify correct tree structure returned

**Implementation Summary:**
- Created FileTreeNode & FileTreeResponse Pydantic schemas with recursive structure
- Implemented efficient O(n) tree-building algorithm in DocumentService
- Added GET /api/projects/{id}/file-tree endpoint with proper error handling
- Comprehensive test coverage: 5 unit tests + 3 integration tests
- Production verified: 99 documents with 8 hierarchical levels

---

### Story 3.2: Implement File Tree Navigation UI ✅ DONE

**Status:** Done (Completed 2025-10-07)
**Story File:** [3.2-implement-file-tree-navigation-ui.md](../stories/3.2-implement-file-tree-navigation-ui.md)
**QA Gate:** PASS (95/100) - [Gate File](../qa/gates/3.2-implement-file-tree-navigation-ui.yml)

**As a** user,
**I want** to see a file tree navigation for browsing documentation,
**so that** I can find and select files to view.

**Acceptance Criteria:**
1. ✅ Explorer page displays split view: file tree (25% width) + content viewer (75% width)
2. ✅ File tree uses react-arborist library for rendering
3. ✅ Folders expandable/collapsible with visual indicators (chevron icons)
4. ✅ File icons differentiate file types (Lucide icons: FileText for .md, Table for .csv, FileCode for .yaml/.json)
5. ✅ Clicking file loads content in viewer pane
6. ✅ Selected file highlighted in tree
7. ✅ Tree scrollable independently of content viewer
8. ✅ Empty state: "No documents synced. Go to Overview and sync a ProjectDoc to get started."
9. ✅ Loading state shown while fetching file tree

**Implementation Summary:**
- Created DocumentationExplorer page with split view layout (25%/75%)
- Implemented FileTreePanel with react-arborist for virtual scrolling
- Added comprehensive state handling (loading, empty, error, success)
- Fixed 3 runtime issues during testing (TypeScript imports, idAccessor, UX)
- Test coverage: 6 unit tests + 3 E2E scenarios (all passing)
- UX improvements: first node auto-expands, entire row clickable for folders

---

### Story 3.3: Build Markdown Renderer with Auto-Generated TOC ✅ DONE

**Status:** Done (Completed 2025-10-08)
**Story File:** [3.3-build-markdown-renderer-with-auto-generated-toc.md](../stories/3.3-build-markdown-renderer-with-auto-generated-toc.md)
**QA Gate:** PASS (95/100) - [Gate File](../qa/gates/3.3-build-markdown-renderer-with-auto-generated-toc.yml)

**As a** user,
**I want** to view markdown files with formatted rendering and a table of contents,
**so that** I can read documentation easily and navigate to sections.

**Acceptance Criteria:**
1. ✅ REST API endpoint `GET /api/documents/{id}` returns document content and metadata
2. ✅ Frontend uses react-markdown with remark/rehype plugins for rendering
3. ✅ Auto-generate TOC from markdown headers (H1-H3) displayed at top of content
4. ✅ TOC links navigate to corresponding sections (smooth scroll)
5. ✅ Syntax highlighting for code blocks using Prism.js (react-prism-renderer)
6. ✅ Support common languages: javascript, typescript, python, bash, json, yaml
7. ✅ Proper styling: headings hierarchy, lists, blockquotes, horizontal rules
8. ✅ Content scrollable within viewer pane
9. ✅ Rendering completes in <1 second for typical BMAD docs (per NFR1)

**Implementation Summary:**
- Created GET /api/documents/{id} endpoint with DocumentService.get_by_id()
- Implemented MarkdownRenderer with react-markdown, remark-gfm, rehype plugins
- Built TableOfContents component with github-slugger for consistent ID generation
- Added syntax highlighting with react-syntax-highlighter (vscDarkPlus theme)
- Configured Tailwind typography plugin for proper markdown styling
- Test coverage: 14 unit tests + 4 E2E tests passing (20 total tests)
- All 12 tasks completed including comprehensive testing and QA validation
- Fixed issues: typography plugin missing, TOC link navigation, TypeScript linting

---

### Story 3.4: Implement Mermaid Diagram Rendering ✅ DONE

**Status:** Done (Completed 2025-10-09)
**Story File:** [3.4-implement-mermaid-diagram-rendering.md](../stories/3.4-implement-mermaid-diagram-rendering.md)
**QA Gate:** PASS - [Gate File](../qa/gates/3.4-implement-mermaid-diagram-rendering.yml)

**As a** user,
**I want** to view Mermaid diagrams embedded in markdown,
**so that** I can see architecture diagrams and flowcharts.

**Acceptance Criteria:**
1. Mermaid code blocks (```mermaid) rendered as diagrams using react-mermaid2
2. Support diagram types: flowchart, sequence, class, state, ER
3. Diagrams render with proper sizing (responsive to content width)
4. Error handling: malformed Mermaid syntax displays error message inline without breaking page
5. Fallback: if Mermaid library fails to load, display code block with warning message
6. Test with sample BMAD architecture docs containing Mermaid diagrams

**Implementation Summary:**
- Created MermaidDiagram component with error handling and responsive design
- Integrated Mermaid rendering into MarkdownRenderer for code blocks
- Dependencies: mermaid (v11.12.0), react-mermaid2 (v0.1.4)
- Test coverage: 6 component tests + 2 integration tests + 1 E2E test (all passing)
- Runtime fix: Dynamic import with proper cleanup and neutral theme
- All acceptance criteria met (AC1-6)

---

### Story 3.6: Implement Cross-Document Navigation ✅ DONE

**Status:** Done (Completed 2025-10-09)
**Story File:** [3.6-implement-cross-document-navigation.md](../stories/3.6-implement-cross-document-navigation.md)
**QA Gate:** PASS (95/100) - [Gate File](../qa/gates/3.6-cross-document-navigation.yml)

**As a** user,
**I want** relative links between markdown files to work,
**so that** I can navigate between related documents seamlessly.

**Acceptance Criteria:**
1. ✅ Markdown links to relative paths (e.g., `[Architecture](./architecture.md)`) resolve to documents in same ProjectDoc
2. ✅ Clicking relative link loads target document in content viewer
3. ✅ File tree updates to highlight newly selected document
4. ✅ Breadcrumb updates to show current file path
5. ✅ Browser history updated (back button works to return to previous document)
6. ✅ Broken links display tooltip: "Document not found" (link disabled)
7. ✅ External links (http://, https://) open in new tab

**Implementation Summary:**
- Created documentService with path normalization logic (O(n) complexity)
- Built useDocumentNavigation hook for browser history and link handling
- Updated MarkdownRenderer to customize anchor element rendering
- Integrated breadcrumb updates and file tree selection synchronization
- Test coverage: 47 unit tests + 8 integration tests + 11 E2E tests (66 total)
- All 7 acceptance criteria validated via comprehensive E2E test suite
- Security: proper external link handling with noopener/noreferrer
- Performance: Navigation completes in <1 second (NFR1)

---

### Story 3.5: Implement CSV Table Viewer [BACKLOG]

**Status:** Deferred to Backlog (P2 - Nice-to-have)

**As a** user,
**I want** to view CSV files as formatted tables,
**so that** I can read structured data clearly.

**Acceptance Criteria:**
1. CSV files parsed and rendered as HTML tables using shadcn/ui Table component
2. Table headers styled distinctly (bold, background color)
3. Table rows alternate background colors for readability
4. Table scrollable horizontally if columns exceed viewer width
5. Table scrollable vertically if rows exceed viewer height
6. Empty cells display as "-" or blank
7. Error handling: malformed CSV displays error message with option to view raw content

**Deferral Rationale:** Independent file type handler, not critical for core documentation viewing functionality. AI Chatbot development takes priority.

---

### Story 3.7: Display YAML, JSON, and TXT Files [BACKLOG]

**Status:** Deferred to Backlog (P2 - Nice-to-have)

**As a** user,
**I want** to view YAML, JSON, and plain text files with proper formatting,
**so that** I can read configuration and data files.

**Acceptance Criteria:**
1. YAML files displayed with syntax highlighting (Prism.js)
2. JSON files displayed with syntax highlighting and proper indentation
3. TXT files displayed in monospace font with preserved whitespace
4. Line numbers displayed for all non-markdown file types
5. Content scrollable within viewer pane
6. Copy button to copy file content to clipboard

**Deferral Rationale:** Independent file type handler, not critical for core documentation viewing functionality. AI Chatbot development takes priority.

---

## Definition of Done - ✅ EPIC COMPLETE

### Must Complete (P0) - ✅ ALL COMPLETE
- [x] Story 3.1: File tree API ✅ (QA: 100/100)
- [x] Story 3.2: File tree navigation UI ✅ (QA: 95/100)
- [x] Story 3.3: Markdown rendering with TOC and syntax highlighting ✅ (QA: 95/100)
- [x] Story 3.4: Mermaid diagram rendering ✅ (QA: PASS)
- [x] Story 3.6: Cross-document navigation works for relative links ✅ (QA: 95/100)
- [x] All completed file types render in <1 second (per NFR1) ✅
- [x] Empty states and error handling implemented ✅
- [x] UI follows shadcn/ui design system ✅

### Deferred to Backlog (P2 - Nice-to-Have)
- [ ] Story 3.5: CSV files render as formatted tables [BACKLOG]
- [ ] Story 3.7: YAML, JSON, TXT files display with proper formatting [BACKLOG]

### Epic Completion Summary
- **Total Stories:** 7 stories defined
- **P0 Stories Completed:** 5/5 (100%)
- **P2 Stories Deferred:** 2 (CSV, YAML/JSON/TXT viewers)
- **Overall QA Score:** 96/100 average (4 stories scored, 1 pending)
- **Test Coverage:** 66 total tests across unit/integration/E2E layers
- **Epic Status:** ✅ **COMPLETE** - Ready for Epic 4

### Next Epic
- **Epic 4: AI Chatbot Development** (ready to begin)
