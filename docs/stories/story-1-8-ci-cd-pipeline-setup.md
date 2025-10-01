# Story 1.8: CI/CD Pipeline Setup

**Status:** Draft

## Story

**As a** developer,
**I want** GitHub Actions CI/CD pipeline for automated testing and quality checks,
**so that** code quality issues are caught early and deployment is automated.

## Acceptance Criteria

1. GitHub Actions workflow file `.github/workflows/ci.yml` created with jobs for frontend and backend
2. Frontend job runs: ESLint checks, TypeScript compilation, Vitest unit tests, build verification
3. Backend job runs: Black formatting check, Ruff linting, pytest with coverage report (target 50%+)
4. Workflow triggers on pull requests and pushes to main branch
5. Workflow completes in under 5 minutes for typical changes
6. Test failures prevent PR merge (required status checks configured)
7. Badge added to README showing build status
8. Optional: Lighthouse CI job for accessibility audit (target score ≥90) runs on frontend changes

## Epic

[Epic 1: Foundation, GitHub Integration & Dashboard Shell](../epics/epic-1-foundation-github-dashboard.md)

## Dependencies

- Story 1.1: Project Infrastructure Setup
- Test frameworks configured in frontend and backend

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
