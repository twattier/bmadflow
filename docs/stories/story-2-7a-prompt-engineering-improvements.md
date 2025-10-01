# Story 2.7a: Prompt Engineering Improvements

**Status:** Draft

## Story

**As a** backend developer,
**I want** to refine extraction prompts based on validation failures,
**so that** extraction accuracy improves.

## Acceptance Criteria

1. Analyze validation results from Story 2.6 to identify top 3 failure patterns
2. Enhance LLM prompts with 5 few-shot examples demonstrating correct extraction
3. Add output format constraints to reduce parsing errors
4. Re-run extraction on 20 failed samples from validation set
5. Validation improvement: achieve ≥80% accuracy on previously failed samples

## Epic

[Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)

## Dependencies

- Story 2.6: Extraction Accuracy Validation Tool (results inform improvements)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
