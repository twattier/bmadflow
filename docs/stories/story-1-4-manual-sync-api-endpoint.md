# Story 1.4: Manual Sync API Endpoint

**Status:** Draft

## Story

**As a** user,
**I want** API endpoint to trigger GitHub repository sync,
**so that** I can manually update BMADFlow with latest documentation changes.

## Acceptance Criteria

1. POST `/api/projects` endpoint accepts JSON body with `github_url` and creates project record in database
2. POST `/api/projects/{project_id}/sync` endpoint triggers background sync task using FastAPI BackgroundTasks
3. Endpoint validates project exists and github_url is accessible before starting sync
4. Sync process: (1) Fetch files from GitHub, (2) Store raw markdown in documents table, (3) Update project last_sync_timestamp
5. Endpoint returns 202 Accepted with sync task ID immediately (doesn't block while syncing)
6. GET `/api/projects/{project_id}/sync-status` endpoint returns current sync progress (status: pending/in_progress/completed/failed, processed_count, total_count, error_message if failed)
7. Sync process stores each document with detected doc_type (infer from file path: `/docs/prd/` = scoping, `/docs/architecture/` = architecture, `/docs/epics/` = epic, `/docs/stories/` = story, `/docs/qa/` = qa, other paths = other)
8. If sync fails, sync-status endpoint includes error_message and retry_allowed flag
9. Integration test confirms: full sync of 50-doc repository completes in <5 minutes, all documents stored correctly

## Epic

[Epic 1: Foundation, GitHub Integration & Dashboard Shell](../epics/epic-1-foundation-github-dashboard.md)

## Dependencies

- Story 1.3: GitHub API Integration - Fetch Repository Files
- Story 1.2: Database Schema for Documents

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
