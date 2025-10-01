# Story 3.8: Sync Status Indicator

**Status:** Draft

## Story

**As a** user,
**I want** persistent sync status indicator in dashboard header,
**so that** I always know if my documentation is up-to-date.

## Acceptance Criteria

1. Header displays last sync timestamp (e.g., "Last synced: 2 hours ago")
2. "Sync Now" button in header triggers manual sync
3. Button disabled during active sync with loading spinner
4. Sync progress displayed as toast notification in top-right (per UX spec): "Syncing... 45 of 100 documents"
5. Toast notification updates every 2 seconds via polling sync-status endpoint
6. On sync complete, toast shows success message: "✓ Sync complete. Extracted 95 of 100 documents." (auto-dismisses after 4 seconds)
7. On sync failure, toast shows error with "Retry" action
8. Dashboard content auto-refreshes after successful sync (React Query cache invalidation)

## Epic

[Epic 3: Multi-View Documentation Dashboard](../epics/epic-3-multi-view-dashboard.md)

## Dependencies

- Story 1.4: Manual Sync API Endpoint (sync-status endpoint)
- Story 1.5: Dashboard Shell with 4-View Navigation (header component)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
