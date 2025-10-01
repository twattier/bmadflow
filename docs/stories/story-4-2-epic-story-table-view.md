# Story 4.2: Epic-Story Table View

**Status:** Draft

## Story

**As a** user,
**I want** table view showing epics and their related stories,
**so that** I can understand project structure without needing graph visualization.

## Acceptance Criteria

1. Epics view includes toggle button: "Graph View" | "Table View" (Table is default for POC)
2. Table view displays hierarchical list: Epic row (bold, status badge) followed by indented Story rows
3. Table columns: Title, Status, Type (Epic/Story), Last Modified
4. Epic rows expandable/collapsible (clicking epic toggles visibility of child stories)
5. All epics expanded by default on initial load
6. Status displayed with color-coded badge (draft=gray, dev=blue, done=green)
7. Clicking any row (epic or story) navigates to Detail view for that document

## Epic

[Epic 4: Epic-Story Relationship Visualization](../epics/epic-4-relationship-visualization.md)

## Dependencies

- Story 4.1: Epic-Story Relationship Data API
- Story 3.6: Epics View - List Display

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
