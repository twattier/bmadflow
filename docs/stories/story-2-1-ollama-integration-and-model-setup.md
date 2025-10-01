# Story 2.1: OLLAMA Integration and Model Setup

**Status:** Draft

## Story

**As a** backend developer,
**I want** OLLAMA configured with selected LLM model,
**so that** extraction pipeline can perform inference on markdown documents.

## Acceptance Criteria

1. OLLAMA service added to Docker Compose configuration (using `ollama/ollama` Docker image)
2. Selected model (from Story 1.7 benchmarking) pulled and loaded in OLLAMA container on startup
3. Python client library (`ollama-python`) installed and configured to communicate with OLLAMA service
4. Extraction service class can send prompt + document text to OLLAMA and receive structured JSON response
5. Service implements retry logic with exponential backoff for transient OLLAMA failures
6. Service includes timeout handling (default 30 sec per document, configurable)
7. Health check endpoint verifies OLLAMA is responding and model is loaded
8. Unit test confirms: service can send test prompt and receive response from OLLAMA

## Epic

[Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)

## Dependencies

- Story 1.7: OLLAMA Model Benchmarking (model selection completed)
- Story 1.1: Project Infrastructure Setup (Docker Compose foundation)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
