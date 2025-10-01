# Story 2.2: User Story Extraction

**Status:** Draft

## Story

**As a** backend developer,
**I want** LLM to extract user story components from story markdown files,
**so that** structured story data can be displayed in the dashboard.

## Acceptance Criteria

1. Extraction service accepts markdown content and document type (story) as input
2. Service generates prompt instructing LLM to extract: (1) "As a" role, (2) "I want" action, (3) "So that" benefit, (4) Acceptance criteria list, (5) Status (draft/dev/done)
3. Service uses Pydantic AI structured output to enforce JSON schema for extracted data
4. Extracted data stored in new `extracted_stories` table with fields: document_id (FK), role, action, benefit, acceptance_criteria (JSONB array), status, confidence_score
5. Service handles extraction failures gracefully (if LLM can't parse, store raw content with status = 'extraction_failed')
6. Developer manually validates extraction on 20 sample story documents from BMAD-METHOD repo

## Epic

[Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)

## Dependencies

- Story 2.1: OLLAMA Integration and Model Setup
- Story 1.2: Database Schema for Documents (extend with extracted_stories table)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
