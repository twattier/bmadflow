# Story 2.3: Epic Extraction

**Status:** Draft

## Story

**As a** backend developer,
**I want** LLM to extract epic metadata from epic markdown files,
**so that** epic information can be displayed and linked to stories.

## Acceptance Criteria

1. Extraction service extracts from epic documents: (1) Epic title, (2) Epic goal/description, (3) Status (draft/dev/done), (4) List of related story filenames (from markdown links like `[Story 1.2](stories/story-1-2.md)`)
2. Extracted data stored in `extracted_epics` table with fields: document_id (FK), title, goal, status, related_stories (JSONB array of story identifiers), confidence_score
3. Service parses markdown links to identify story relationships and stores in `relationships` table (parent = epic document_id, child = story document_id resolved from filename, relationship_type = 'contains')
4. Link resolution handles both relative paths (`stories/story-1-2.md`) and absolute paths (`/docs/stories/story-1-2.md`)
5. Unresolved links (story file doesn't exist) logged as warnings but don't fail extraction
6. Developer validates on 10 sample epic documents

## Epic

[Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)

## Dependencies

- Story 2.1: OLLAMA Integration and Model Setup
- Story 1.2: Database Schema for Documents (relationships table)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
