# Story 3.2: Detail View - Markdown Rendering

**Status:** Draft

## Story

**As a** user,
**I want** Detail view to render markdown content beautifully,
**so that** reading documentation in BMADFlow is significantly better than GitHub.

## Acceptance Criteria

1. Detail view fetches single document content from `/api/documents/{id}` endpoint
2. Markdown rendered using react-markdown library with remark plugins (GitHub Flavored Markdown support)
3. Rendered content includes: headers (h1-h6), paragraphs, lists (ordered/unordered), tables, blockquotes, inline code, code blocks, links, images
4. Code blocks have syntax highlighting using Prism.js or similar (supports TypeScript, Python, JavaScript, YAML, JSON)
5. Each code block includes "Copy" button in top-right corner
6. Content area has max-width constraint (1280px per UX spec) for readability
7. Typography uses Inter font with 1.5 line height for body text

## Epic

[Epic 3: Multi-View Documentation Dashboard](../epics/epic-3-multi-view-dashboard.md)

## Dependencies

- Story 1.5: Dashboard Shell with 4-View Navigation (Detail view route)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
