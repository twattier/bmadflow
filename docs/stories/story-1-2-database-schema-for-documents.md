# Story 1.2: Database Schema for Documents

**Status:** Draft

## Story

**As a** backend developer,
**I want** PostgreSQL schema to store projects, documents, and their metadata,
**so that** synced GitHub content can be persisted and queried.

## Acceptance Criteria

1. Database migration creates `projects` table with fields: id (UUID), name, github_url, last_sync_timestamp, created_at
2. Database migration creates `documents` table with fields: id (UUID), project_id (FK), file_path, content (TEXT), doc_type (enum: scoping/architecture/epic/story/qa/other), last_modified, created_at
3. Database migration creates `relationships` table with fields: id (UUID), parent_doc_id (FK), child_doc_id (FK), relationship_type (enum: contains/relates_to), created_at
4. pgvector extension installed and `documents` table has `embedding` column (vector(384)) for future semantic search
5. Indexes created on commonly queried fields (project_id, file_path, doc_type)
6. Migration can be run with `alembic upgrade head` command

## Epic

[Epic 1: Foundation, GitHub Integration & Dashboard Shell](../epics/epic-1-foundation-github-dashboard.md)

## Dependencies

- Story 1.1: Project Infrastructure Setup (database service must be running)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
