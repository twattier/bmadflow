# Story 1.6: Project Setup and Sync UI

**Status:** Draft

## Story

**As a** user,
**I want** UI to add GitHub repository and trigger sync,
**so that** I can load my documentation into BMADFlow.

## Acceptance Criteria

1. Landing page displays "Add Project" form with input field for GitHub URL and "Sync Now" button
2. Input validation shows error if URL format incorrect (must match `github.com/org/repo` pattern)
3. Clicking "Sync Now" calls POST `/api/projects` with github_url, then immediately calls POST `/api/projects/{id}/sync`
4. Form disabled during sync with loading spinner and "Syncing..." message
5. Sync progress shown via polling GET `/api/projects/{id}/sync-status` every 2 seconds
6. Progress display shows: "Syncing... X of Y documents processed"
7. On sync complete (status = completed), redirect to `/scoping` view
8. On sync failure (status = failed), display error message with "Retry" button that calls POST /sync endpoint again
9. After successful sync, project name appears in top navigation bar
10. Manual test confirms: adding `github.com/bmad-code-org/BMAD-METHOD` repo completes sync flow end-to-end

## Epic

[Epic 1: Foundation, GitHub Integration & Dashboard Shell](../epics/epic-1-foundation-github-dashboard.md)

## Dependencies

- Story 1.4: Manual Sync API Endpoint
- Story 1.5: Dashboard Shell with 4-View Navigation

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
