# Story 4.1: Epic-Story Relationship Data API

**Status:** Draft

## Story

**As a** frontend developer,
**I want** API endpoint returning epic-story relationship graph data,
**so that** I can build visualization components.

## Acceptance Criteria

1. GET `/api/projects/{id}/relationships` endpoint returns JSON representing epic-story graph
2. Response format: `{ nodes: [ {id, title, type: 'epic'|'story', status, document_id} ], edges: [ {source_id, target_id, type: 'contains'} ] }`
3. Nodes include extracted epic/story data (title from extracted_epics/extracted_stories, status for color-coding)
4. Edges derived from relationships table (epic → stories links)
5. Endpoint includes optional query param `?epic_id=` to filter graph to single epic and its stories
6. Response cached with 5-minute TTL (Redis cache)

## Epic

[Epic 4: Epic-Story Relationship Visualization](../epics/epic-4-relationship-visualization.md)

## Dependencies

- Story 2.3: Epic Extraction (relationships data)
- Story 2.2: User Story Extraction
- Story 1.2: Database Schema for Documents (relationships table)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
