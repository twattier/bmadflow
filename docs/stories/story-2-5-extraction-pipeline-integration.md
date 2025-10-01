# Story 2.5: Extraction Pipeline Integration

**Status:** Draft

## Story

**As a** backend developer,
**I want** extraction automatically triggered after GitHub sync completes,
**so that** extracted data is available immediately without manual step.

## Acceptance Criteria

1. Sync process (from Story 1.4) extended: after storing raw documents, trigger extraction for each document
2. Extraction runs for all documents with doc_type = epic or story (scoping/architecture documents extracted in Epic 3)
3. Extraction parallelized: process 4 documents concurrently to reduce total time
4. Sync status endpoint updated to show extraction progress (syncing/extracting/complete phases)
5. Failed extractions logged with document_id and error message, but don't fail entire sync
6. Extraction results summary included in sync completion: total documents, successfully extracted, extraction failures, average confidence score
7. Integration test confirms: syncing 50-doc repo triggers extraction for all epics/stories, completes in <10 minutes (including OLLAMA inference time)

## Epic

[Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)

## Dependencies

- Story 2.2: User Story Extraction
- Story 2.3: Epic Extraction
- Story 2.4: Status Detection
- Story 1.4: Manual Sync API Endpoint

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
