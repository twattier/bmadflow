# Story 1.3: GitHub API Integration - Fetch Repository Files

**Status:** Draft

## Story

**As a** backend developer,
**I want** service to fetch markdown files from public GitHub repositories,
**so that** users can sync their documentation into BMADFlow.

## Acceptance Criteria

1. GitHub service class accepts repository URL (format: `github.com/org/repo`) and validates format
2. Service requires GitHub Personal Access Token as parameter (stored in environment variables)
3. Service fetches repository tree from `/docs` folder using GitHub REST API v3
4. Service recursively retrieves all `.md` files and their content
5. Service handles GitHub API errors gracefully (404 not found, 403 rate limit, network errors) with descriptive error messages
6. Manual test confirms: can fetch all docs from `github.com/bmad-code-org/BMAD-METHOD` repo in <2 minutes

## Epic

[Epic 1: Foundation, GitHub Integration & Dashboard Shell](../epics/epic-1-foundation-github-dashboard.md)

## Dependencies

- Story 1.2: Database Schema for Documents (for storing fetched files)
- GitHub Personal Access Token configured in environment

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
