# Epic 2: LLM-Powered Content Extraction

**Status:** Draft

## Epic Goal

Implement OLLAMA-based extraction of structured information from BMAD markdown (user stories, epics, status, relationships). Developer validates extraction logic on 20 sample documents in Week 2. PM/pilot users perform comprehensive 100-document accuracy validation in parallel with Epic 3 (async validation, results inform Epic 3 refinements).

## Epic Description

This epic delivers the core AI-powered intelligence of BMADFlow: extracting structured data from unstructured BMAD markdown files using OLLAMA LLM. By the end of this epic, the system can automatically identify user story components ("As a/I want/So that"), acceptance criteria, epic goals, status indicators (draft/dev/done), and epic-to-story relationships from markdown links.

The epic includes comprehensive extraction accuracy validation (Story 2.6) targeting 90%+ accuracy, with prompt engineering improvements (Stories 2.7a-c) to address any shortfalls. Extraction runs automatically after GitHub sync, making structured data immediately available for dashboard visualization.

**Prerequisites:** Week 1 Story 1.7 completed - GPU availability confirmed and model selected based on benchmarking.

## Stories

### Story 2.1: OLLAMA Integration and Model Setup

As a **backend developer**,
I want **OLLAMA configured with selected LLM model**,
so that **extraction pipeline can perform inference on markdown documents**.

**Acceptance Criteria:**

1. OLLAMA service added to Docker Compose configuration (using `ollama/ollama` Docker image)
2. Selected model (from Story 1.7 benchmarking) pulled and loaded in OLLAMA container on startup
3. Python client library (`ollama-python`) installed and configured to communicate with OLLAMA service
4. Extraction service class can send prompt + document text to OLLAMA and receive structured JSON response
5. Service implements retry logic with exponential backoff for transient OLLAMA failures
6. Service includes timeout handling (default 30 sec per document, configurable)
7. Health check endpoint verifies OLLAMA is responding and model is loaded
8. Unit test confirms: service can send test prompt and receive response from OLLAMA

### Story 2.2: User Story Extraction

As a **backend developer**,
I want **LLM to extract user story components from story markdown files**,
so that **structured story data can be displayed in the dashboard**.

**Acceptance Criteria:**

1. Extraction service accepts markdown content and document type (story) as input
2. Service generates prompt instructing LLM to extract: (1) "As a" role, (2) "I want" action, (3) "So that" benefit, (4) Acceptance criteria list, (5) Status (draft/dev/done)
3. Service uses Pydantic AI structured output to enforce JSON schema for extracted data
4. Extracted data stored in new `extracted_stories` table with fields: document_id (FK), role, action, benefit, acceptance_criteria (JSONB array), status, confidence_score
5. Service handles extraction failures gracefully (if LLM can't parse, store raw content with status = 'extraction_failed')
6. Developer manually validates extraction on 20 sample story documents from BMAD-METHOD repo

### Story 2.3: Epic Extraction

As a **backend developer**,
I want **LLM to extract epic metadata from epic markdown files**,
so that **epic information can be displayed and linked to stories**.

**Acceptance Criteria:**

1. Extraction service extracts from epic documents: (1) Epic title, (2) Epic goal/description, (3) Status (draft/dev/done), (4) List of related story filenames (from markdown links like `[Story 1.2](stories/story-1-2.md)`)
2. Extracted data stored in `extracted_epics` table with fields: document_id (FK), title, goal, status, related_stories (JSONB array of story identifiers), confidence_score
3. Service parses markdown links to identify story relationships and stores in `relationships` table (parent = epic document_id, child = story document_id resolved from filename, relationship_type = 'contains')
4. Link resolution handles both relative paths (`stories/story-1-2.md`) and absolute paths (`/docs/stories/story-1-2.md`)
5. Unresolved links (story file doesn't exist) logged as warnings but don't fail extraction
6. Developer validates on 10 sample epic documents

### Story 2.4: Status Detection

As a **backend developer**,
I want **LLM to detect document status indicators**,
so that **dashboard can display color-coded status (draft/dev/done)**.

**Acceptance Criteria:**

1. Extraction service detects status from explicit markers in markdown: `Status: Draft`, `Status: Dev`, `Status: Done` (case-insensitive, various formats supported)
2. If no explicit status, LLM infers status from content analysis (acceptance criteria complete = likely dev/done, TODOs present = likely draft)
3. Status enum standardized to: draft, dev, done (maps to colors: gray, blue, green per UX spec)
4. Status stored in extracted_stories and extracted_epics tables
5. Developer validates status detection on 20 documents with known status labels
6. Validation target: 90%+ accuracy on documents with explicit status markers, 70%+ on documents requiring inference

### Story 2.5: Extraction Pipeline Integration

As a **backend developer**,
I want **extraction automatically triggered after GitHub sync completes**,
so that **extracted data is available immediately without manual step**.

**Acceptance Criteria:**

1. Sync process (from Story 1.4) extended: after storing raw documents, trigger extraction for each document
2. Extraction runs for all documents with doc_type = epic or story (scoping/architecture documents extracted in Epic 3)
3. Extraction parallelized: process 4 documents concurrently to reduce total time
4. Sync status endpoint updated to show extraction progress (syncing/extracting/complete phases)
5. Failed extractions logged with document_id and error message, but don't fail entire sync
6. Extraction results summary included in sync completion: total documents, successfully extracted, extraction failures, average confidence score
7. Integration test confirms: syncing 50-doc repo triggers extraction for all epics/stories, completes in <10 minutes (including OLLAMA inference time)

### Story 2.6: Extraction Accuracy Validation Tool

As a **PM/QA**,
I want **tool to validate extraction accuracy against ground truth**,
so that **we can measure whether 90% accuracy target is achieved**.

**Acceptance Criteria:**

1. CLI tool `python scripts/validate_extraction.py` accepts: (1) Project ID, (2) CSV file with ground truth labels (document_id, expected_role, expected_action, expected_status, etc.)
2. Tool queries extracted_stories and extracted_epics tables for specified project
3. Tool compares extracted values against ground truth and calculates per-field accuracy (role accuracy, action accuracy, status accuracy, overall accuracy)
4. Tool outputs validation report: total documents, correctly extracted (all fields match), partially correct (some fields match), failed, accuracy percentage per field
5. PM uses tool to validate 100-document test set (ground truth labels created manually)
6. Validation results documented in `docs/extraction-validation-results.md` with accuracy breakdown
7. Success criteria: Overall accuracy ≥90% on 100-document test set (if <90%, Stories 2.7a-c address improvements)

### Story 2.7a: Prompt Engineering Improvements

As a **backend developer**,
I want **to refine extraction prompts based on validation failures**,
so that **extraction accuracy improves**.

**Acceptance Criteria:**

1. Analyze validation results from Story 2.6 to identify top 3 failure patterns
2. Enhance LLM prompts with 5 few-shot examples demonstrating correct extraction
3. Add output format constraints to reduce parsing errors
4. Re-run extraction on 20 failed samples from validation set
5. Validation improvement: achieve ≥80% accuracy on previously failed samples

### Story 2.7b: Status Detection Fallback Rules

As a **backend developer**,
I want **regex-based fallback for status detection**,
so that **status accuracy improves when LLM inference is uncertain**.

**Acceptance Criteria:**

1. Add regex patterns for common status markers: "Status: X", "[STATUS: X]", "<!-- status: X -->"
2. If LLM confidence score <0.7, use regex fallback
3. Re-run validation on status field
4. Status detection accuracy improves to ≥85%

### Story 2.7c: Acceptance Criteria Parsing

As a **backend developer**,
I want **numbered list parser for acceptance criteria**,
so that **AC extraction accuracy improves**.

**Acceptance Criteria:**

1. Add structured parser for common AC formats: "1. AC text", "- AC text", "AC1: text"
2. If LLM fails to extract ACs (empty result), use structured parser as fallback
3. Re-run validation on AC field
4. AC extraction accuracy improves to ≥85%

## Dependencies

- Epic 1 Story 1.7: OLLAMA model selected and benchmarked
- Epic 1 Story 1.2: Database schema with extracted_stories/extracted_epics tables
- Epic 1 Story 1.4: GitHub sync pipeline functional
- External OLLAMA server with GPU recommended for <10 min sync times

## Success Metrics

- 90%+ extraction accuracy on 100-document validation set
- Extraction completes in <10 minutes for 50-document repository
- Zero critical extraction failures that block sync
- All extracted data available via API for dashboard views

## Timeline

**Target:** Week 2 of POC (5 working days)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Epic extracted from PRD v1.0 | Sarah (PO) |
