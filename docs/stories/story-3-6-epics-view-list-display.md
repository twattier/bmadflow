# Story 3.6: Epics View - List Display

**Status:** Draft

## Story

**As a** user,
**I want** Epics view to show list of all epics with status indicators,
**so that** I can see project epic structure at a glance.

## Acceptance Criteria

1. Epics view fetches documents where doc_type = 'epic' from API
2. Epics displayed as list (table or card list) with columns: Epic Title, Status, Story Count, Last Modified
3. Status displayed with color-coded badge: Draft (gray), Dev (blue), Done (green) per UX spec
4. Story Count calculated from relationships table (count child documents where relationship_type = 'contains')
5. Clicking epic row navigates to Detail view showing full epic content
6. Epics sorted by filename/number (e.g., Epic 1, Epic 2, Epic 3) for logical sequence
7. Status rollup widget displayed at top: "X epics total | Y draft, Z in dev, W done"

## Epic

[Epic 3: Multi-View Documentation Dashboard](../epics/epic-3-multi-view-dashboard.md)

## Dependencies

- Story 2.3: Epic Extraction (extracted epic data)
- Story 1.5: Dashboard Shell with 4-View Navigation

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
