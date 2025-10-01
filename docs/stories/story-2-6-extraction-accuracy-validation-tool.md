# Story 2.6: Extraction Accuracy Validation Tool

**Status:** Draft

## Story

**As a** PM/QA,
**I want** tool to validate extraction accuracy against ground truth,
**so that** we can measure whether 90% accuracy target is achieved.

## Acceptance Criteria

1. CLI tool `python scripts/validate_extraction.py` accepts: (1) Project ID, (2) CSV file with ground truth labels (document_id, expected_role, expected_action, expected_status, etc.)
2. Tool queries extracted_stories and extracted_epics tables for specified project
3. Tool compares extracted values against ground truth and calculates per-field accuracy (role accuracy, action accuracy, status accuracy, overall accuracy)
4. Tool outputs validation report: total documents, correctly extracted (all fields match), partially correct (some fields match), failed, accuracy percentage per field
5. PM uses tool to validate 100-document test set (ground truth labels created manually)
6. Validation results documented in `docs/extraction-validation-results.md` with accuracy breakdown
7. Success criteria: Overall accuracy ≥90% on 100-document test set (if <90%, Stories 2.7a-c address improvements)

## Epic

[Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)

## Dependencies

- Story 2.5: Extraction Pipeline Integration
- Ground truth dataset (100 manually labeled documents)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
