# Story 3.1: Scoping View - Document Cards Grid

**Status:** Draft

## Story

**As a** user,
**I want** Scoping view to display grid of scoping documents as cards,
**so that** I can quickly see all research, PRD, and use case documents.

## Acceptance Criteria

1. Scoping view fetches documents where doc_type = 'scoping' from `/api/projects/{id}/documents?type=scoping` endpoint
2. Documents displayed as card grid (3 columns on desktop per UX spec)
3. Each card shows: document title (extracted from first H1 heading), excerpt (first 150 characters of content), last modified date, status badge if available
4. Cards are clickable - clicking navigates to Detail view with document_id parameter
5. Cards show visual loading state (skeleton placeholders) while data fetches
6. Empty state displayed if no scoping documents found: "No scoping documents found. Check repository structure."
7. Search/filter input at top of grid (filters document titles as user types - simple client-side filtering for POC)

## Epic

[Epic 3: Multi-View Documentation Dashboard](../epics/epic-3-multi-view-dashboard.md)

## Dependencies

- Story 1.5: Dashboard Shell with 4-View Navigation
- Story 1.4: Manual Sync API Endpoint (documents API)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
