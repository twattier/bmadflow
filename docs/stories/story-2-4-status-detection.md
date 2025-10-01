# Story 2.4: Status Detection

**Status:** Draft

## Story

**As a** backend developer,
**I want** LLM to detect document status indicators,
**so that** dashboard can display color-coded status (draft/dev/done).

## Acceptance Criteria

1. Extraction service detects status from explicit markers in markdown: `Status: Draft`, `Status: Dev`, `Status: Done` (case-insensitive, various formats supported)
2. If no explicit status, LLM infers status from content analysis (acceptance criteria complete = likely dev/done, TODOs present = likely draft)
3. Status enum standardized to: draft, dev, done (maps to colors: gray, blue, green per UX spec)
4. Status stored in extracted_stories and extracted_epics tables
5. Developer validates status detection on 20 documents with known status labels
6. Validation target: 90%+ accuracy on documents with explicit status markers, 70%+ on documents requiring inference

## Epic

[Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)

## Dependencies

- Story 2.2: User Story Extraction
- Story 2.3: Epic Extraction

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
