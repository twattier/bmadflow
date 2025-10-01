# Story 3.3: Detail View - Table of Contents

**Status:** Draft

## Story

**As a** user,
**I want** Table of Contents sidebar in Detail view,
**so that** I can quickly jump to specific sections in long documents.

## Acceptance Criteria

1. TOC automatically generated from document headings (H2 and H3 levels included)
2. TOC displayed in left sidebar (256px width per UX spec, collapsible on narrow screens)
3. TOC items clickable - clicking scrolls to corresponding section with smooth animation (400ms per UX spec)
4. Active section highlighted in TOC based on scroll position (heading currently visible at top of viewport)
5. TOC shows hierarchical structure (H2 as parent, H3 nested with indentation)
6. TOC sticky positioned (stays visible while scrolling main content)
7. Empty state: TOC hidden if document has <3 headings

## Epic

[Epic 3: Multi-View Documentation Dashboard](../epics/epic-3-multi-view-dashboard.md)

## Dependencies

- Story 3.2: Detail View - Markdown Rendering

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
