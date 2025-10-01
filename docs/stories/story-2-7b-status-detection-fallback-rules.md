# Story 2.7b: Status Detection Fallback Rules

**Status:** Draft

## Story

**As a** backend developer,
**I want** regex-based fallback for status detection,
**so that** status accuracy improves when LLM inference is uncertain.

## Acceptance Criteria

1. Add regex patterns for common status markers: "Status: X", "[STATUS: X]", "<!-- status: X -->"
2. If LLM confidence score <0.7, use regex fallback
3. Re-run validation on status field
4. Status detection accuracy improves to ≥85%

## Epic

[Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)

## Dependencies

- Story 2.6: Extraction Accuracy Validation Tool (results inform improvements)
- Story 2.4: Status Detection

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
