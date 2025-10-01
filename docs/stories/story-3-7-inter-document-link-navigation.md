# Story 3.7: Inter-Document Link Navigation

**Status:** Draft

## Story

**As a** user,
**I want** markdown links to other documents to navigate within BMADFlow,
**so that** I can explore related documentation without leaving the dashboard.

## Acceptance Criteria

1. Markdown rendering (Story 3.2) detects links to `.md` files (e.g., `[Architecture](../architecture.md)`)
2. Link resolver service maps file paths to document IDs in database
3. Links rewritten to navigate to Detail view route: `/detail/{document_id}` using React Router Link component
4. Clicking inter-document link navigates within SPA (no page reload)
5. Breadcrumb navigation updated to show: Project > Current View > Document Title
6. External links (http/https) open in new tab with `target="_blank" rel="noopener"`
7. Broken links (reference non-existent document) styled differently (red text) with tooltip: "Document not found"

## Epic

[Epic 3: Multi-View Documentation Dashboard](../epics/epic-3-multi-view-dashboard.md)

## Dependencies

- Story 3.2: Detail View - Markdown Rendering
- Story 1.2: Database Schema for Documents (for link resolution)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
