# Story 1.1: Project Infrastructure Setup

**Status:** Draft

## Story

**As a** developer,
**I want** Docker Compose configuration with all required services,
**so that** I can run the entire application locally with a single command.

## Acceptance Criteria

1. Docker Compose file defines services: frontend (Vite dev server), backend (FastAPI), postgres (with pgvector extension)
2. Running `docker-compose up` starts all services successfully
3. Services can communicate (frontend can reach backend API, backend can connect to database)
4. Volume mounts configured for hot reload during development (code changes reflect without rebuild)
5. Environment variables documented in `.env.example` file
6. README includes "Getting Started" section with setup instructions (prerequisites, commands)
7. Health check endpoint `/api/health` returns 200 OK when backend is ready
8. Dependency conflict check: `npm install` completes without peer dependency warnings, `pip install` completes without version conflicts

## Epic

[Epic 1: Foundation, GitHub Integration & Dashboard Shell](../epics/epic-1-foundation-github-dashboard.md)

## Dependencies

- Docker 24.0+
- Node 20+
- Python 3.11+

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
