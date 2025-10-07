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

## Story Sequencing & Dependencies

### Critical Path (Sequential - Cannot Parallelize)
```
Story 3.1 (File Tree API) ← START HERE
    ↓
Story 3.2 (File Tree UI) ← Depends on 3.1 API
    ↓
Story 3.3 (Markdown Renderer) ← Depends on 3.2 viewer pane
    ↓
Story 3.6 (Cross-Doc Navigation) ← Depends on 3.3 functional renderer
```

### Parallelizable Stories (After Story 3.3)
Once Story 3.3 is complete, these can be developed in parallel:
- **Story 3.4** (Mermaid Diagrams) - Extends markdown renderer
- **Story 3.5** (CSV Viewer) - Independent file type handler
- **Story 3.7** (YAML/JSON/TXT) - Independent file type handler

### Dependency Summary
| Story | Depends On | Can Start After | Estimated Days |
|-------|------------|-----------------|----------------|
| 3.1 | Epic 2 complete | Immediately (after checklist) | 1-2 days |
| 3.2 | Story 3.1 | Day 2-3 | 1-2 days |
| 3.3 | Story 3.2 | Day 3-4 | 2 days |
| 3.4 | Story 3.3 | Day 5-6 | 0.5 day |
| 3.5 | Story 3.3 | Day 5-6 (parallel with 3.4) | 0.5 day |
| 3.7 | Story 3.3 | Day 5-6 (parallel with 3.4, 3.5) | 0.5 day |
| 3.6 | Story 3.3 | Day 6-7 | 1 day |

**Total Estimated Duration**: 7-9 days

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

### Story 3.4: Implement Mermaid Diagram Rendering

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

---

### Story 3.5: Implement CSV Table Viewer

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

---

### Story 3.6: Implement Cross-Document Navigation

**As a** user,
**I want** relative links between markdown files to work,
**so that** I can navigate between related documents seamlessly.

**Acceptance Criteria:**
1. Markdown links to relative paths (e.g., `[Architecture](./architecture.md)`) resolve to documents in same ProjectDoc
2. Clicking relative link loads target document in content viewer
3. File tree updates to highlight newly selected document
4. Breadcrumb updates to show current file path
5. Browser history updated (back button works to return to previous document)
6. Broken links display tooltip: "Document not found" (link disabled)
7. External links (http://, https://) open in new tab

---

### Story 3.7: Display YAML, JSON, and TXT Files

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

---

## Definition of Done

- [ ] All 7 stories completed with acceptance criteria met
- [ ] File tree navigation working smoothly with expand/collapse
- [ ] Markdown rendering with TOC, syntax highlighting, and Mermaid diagrams
- [ ] CSV files render as formatted tables
- [ ] YAML, JSON, TXT files display with proper formatting
- [ ] Cross-document navigation works for relative links
- [ ] All file types render in <1 second (per NFR1)
- [ ] Empty states and error handling implemented
- [ ] UI follows shadcn/ui design system
