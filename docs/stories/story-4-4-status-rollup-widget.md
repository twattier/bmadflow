# Story 4.4: Status Rollup Widget

**Status:** Draft

## Story

**As a** user,
**I want** status summary widget in Epics view,
**so that** I can see project health at a glance.

## Acceptance Criteria

1. Widget displayed prominently in Epics view (top-right sidebar per UX spec)
2. Widget shows: "X epics | Y stories"
3. Widget shows status breakdown: "Z draft, W in dev, V done"
4. Status counts derived from extracted_epics and extracted_stories tables
5. Widget shows percentage complete: "(V/Y stories done = X%)"
6. Visual progress bar shows completion percentage (green fill)

## Epic

[Epic 4: Epic-Story Relationship Visualization](../epics/epic-4-relationship-visualization.md)

## Dependencies

- Story 4.1: Epic-Story Relationship Data API
- Story 2.2: User Story Extraction
- Story 2.3: Epic Extraction

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
