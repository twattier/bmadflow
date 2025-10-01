# Story 4.5: Search/Filter Across Epics and Stories

**Status:** Draft

## Story

**As a** user,
**I want** search functionality to find specific epics or stories by keyword,
**so that** I can quickly locate information without browsing entire graph.

## Acceptance Criteria

1. Search input field at top of Epics view (consistent with Scoping view from Story 3.1)
2. Search filters both epics and stories by title match (case-insensitive substring search)
3. Table view: Filtered results show matching epics/stories, other rows hidden
4. Graph view: Filtered results highlight matching nodes (dimmed/grayed out non-matches)
5. Search is client-side for POC (filters already-loaded data, no server query)
6. Clear button (X icon) in search input resets filter
7. Debounced input (300ms delay) to avoid re-filtering on every keystroke

## Epic

[Epic 4: Epic-Story Relationship Visualization](../epics/epic-4-relationship-visualization.md)

## Dependencies

- Story 4.2: Epic-Story Table View
- Story 3.1: Scoping View - Document Cards Grid (search pattern)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
