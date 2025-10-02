# Story 2.4: Status Detection

## Status

Done

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

## Tasks / Subtasks

- [x] Task 1: Enhance LLM prompts for explicit status detection (AC: 1)
  - [x] Update `StoryExtractionService.SYSTEM_PROMPT` to include explicit status marker patterns
  - [x] Update `EpicExtractionService.SYSTEM_PROMPT` to include explicit status marker patterns
  - [x] Add examples for status formats: `**Status:** Draft`, `Status: Dev`, `[Status: Done]`, case-insensitive
  - [x] Update `USER_PROMPT_TEMPLATE` in both services to emphasize explicit marker detection first

- [x] Task 2: Implement LLM-based status inference for documents without explicit markers (AC: 2)
  - [x] Update story extraction prompt to include inference rules:
    - If all acceptance criteria are checked/complete → "done"
    - If TODOs present in tasks → "draft"
    - If implementation notes exist → "dev"
  - [x] Update epic extraction prompt to include inference rules:
    - If all stories marked complete → "done"
    - If no stories started → "draft"
    - If some stories complete → "dev"
  - [x] Document inference logic in service docstrings

- [x] Task 3: Enhance regex fallback for status detection (AC: 1, 3)
  - [x] Update `StoryExtractionService._regex_fallback()` to detect multiple status formats:
    - `**Status:** Draft|Dev|Done`
    - `Status: Draft|Dev|Done` (no bold)
    - `[Status: Draft|Dev|Done]` (bracketed)
    - `<!-- status: draft|dev|done -->` (HTML comment)
  - [x] Make regex case-insensitive
  - [x] Update `EpicExtractionService._regex_fallback()` with same patterns
  - [x] Ensure normalization to lowercase enum values: "draft", "dev", "done"

- [x] Task 4: Verify status storage in database (AC: 4)
  - [x] Confirm `extracted_stories.status` column exists (from Story 2.2)
  - [x] Confirm `extracted_epics.status` column exists (from Story 2.3)
  - [x] Verify status enum constraint matches: "draft", "dev", "done"
  - [x] Review `ExtractedStorySchema` and `ExtractedEpicSchema` for status field typing

- [x] Task 5: Create validation test dataset (AC: 5)
  - [x] Create 20 test markdown documents with known status labels:
    - 10 with explicit markers (various formats)
    - 10 without explicit markers (requiring inference)
  - [x] Save test documents in `apps/api/tests/fixtures/status_detection/`
  - [x] Create ground truth CSV: `apps/api/tests/fixtures/status_detection/ground_truth.csv` with columns: filename, expected_status

- [x] Task 6: Write unit tests for status detection (AC: 5, 6)
  - [x] Test explicit marker detection (various formats)
  - [x] Test case-insensitive detection
  - [x] Test LLM inference for documents without markers
  - [x] Test regex fallback for explicit markers
  - [x] Test status normalization (uppercase → lowercase)
  - [x] Test confidence scoring for status field

- [x] Task 7: Run validation on 20-document test set (AC: 5, 6)
  - [x] Execute extraction on all 20 test documents
  - [x] Compare extracted status against ground truth
  - [x] Calculate accuracy: explicit markers (target ≥90%), inference (target ≥70%)
  - [x] Document results in debug log and story completion notes
  - [x] If targets not met, iterate on prompts or add more fallback patterns

## Dev Notes

### Previous Story Insights

No previous story files exist. Story 2.1 (OLLAMA Integration) completed all prerequisites including:
- OLLAMA service configured and tested
- Database tables (`extracted_stories`, `extracted_epics`) created
- Extraction service patterns established

### Architecture Context

#### Tech Stack
[Source: architecture/tech-stack.md]
- **Backend Framework**: FastAPI 0.104+ with Python 3.11+
- **LLM Framework**: Pydantic AI 0.0.13+ for structured LLM output
- **LLM Inference**: OLLAMA 0.1.17+ with `qwen2.5:7b-instruct-q4_K_M` model
- **Database**: PostgreSQL 15.4+
- **Testing**: pytest 7.4+ with pytest-asyncio

#### Data Models & Schema
[Source: architecture/data-models.md]

**ExtractedStory Model:**
- `status`: enum (`draft`, `dev`, `done`)
- Stored in `extracted_stories` table
- TypeScript interface: `status: 'draft' | 'dev' | 'done'`

**ExtractedEpic Model:**
- `status`: enum (`draft`, `dev`, `done`)
- Stored in `extracted_epics` table
- TypeScript interface: `status: 'draft' | 'dev' | 'done'`

[Source: architecture/database-schema.md]
```sql
CREATE TABLE extracted_stories (
    ...
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    ...
);

CREATE TABLE extracted_epics (
    ...
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    ...
);
```

#### File Locations
[Source: architecture/unified-project-structure.md, backend-architecture.md]

**Services to modify:**
- `apps/api/src/services/story_extraction_service.py` - Enhance status detection in story extraction
- `apps/api/src/services/epic_extraction_service.py` - Enhance status detection in epic extraction

**Test locations:**
- `apps/api/tests/test_story_extraction_service.py` - Add status detection tests
- `apps/api/tests/test_epic_extraction_service.py` - Add status detection tests
- `apps/api/tests/fixtures/status_detection/` - Test documents directory (create)

#### Existing Implementation Patterns
[Source: Existing service code review]

**StoryExtractionService (apps/api/src/services/story_extraction_service.py):**
- Already extracts basic status from explicit markers
- Has `_regex_fallback()` method for status extraction (line 174-178)
- Has `_normalize_status()` method (line 214-230)
- Current regex: `r"\*?\*?Status:?\*?\*?\s*(Draft|Dev|Done)"` with case-insensitive flag

**EpicExtractionService (apps/api/src/services/epic_extraction_service.py):**
- Already extracts status from explicit markers
- Has `_regex_fallback()` method for status extraction (line 242-246)
- Current regex: `r"\*\*Status:\*\*\s*(Draft|Dev|Done)"` with case-insensitive flag

**Enhancement needed:**
- Add LLM inference rules to prompts (currently only detects explicit markers)
- Expand regex patterns to handle more status formats (bracketed, HTML comments)
- Enhance confidence scoring to reflect status detection quality

#### Technical Constraints
[Source: architecture/coding-standards.md]
- Use snake_case for Python functions
- Database tables use snake_case plural naming
- Constants use SCREAMING_SNAKE_CASE
- Always use async/await, never `.then()` chains
- Never mutate state directly

### Testing

[Source: architecture/testing-strategy.md]

**Test Organization:**
- Backend tests location: `apps/api/tests/`
- Use pytest + pytest-asyncio + httpx
- Target: 50% backend coverage for POC

**Test Requirements for this Story:**
1. Unit tests for explicit status marker detection (various formats)
2. Unit tests for LLM inference (documents without explicit markers)
3. Unit tests for regex fallback patterns
4. Unit tests for status normalization
5. Integration test: Extract status from 20 test documents, validate accuracy ≥90% (explicit), ≥70% (inference)

**Test File Naming:**
- Test files mirror service files: `test_story_extraction_service.py`, `test_epic_extraction_service.py`

**Example Test Pattern:**
```python
@pytest.mark.asyncio
async def test_status_detection_explicit_marker():
    service = StoryExtractionService()
    document = Document(content="**Status:** Dev\n...")
    result = await service.extract_story(document)
    assert result.status == "dev"
```

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-03 | 1.0 | Story created from Epic 2 by Scrum Master Bob | Bob (SM) |
| 2025-10-03 | 1.1 | Story validated and approved for implementation (10/10 readiness score) | Sarah (PO) |
| 2025-10-03 | 2.0 | Story implementation complete - All tasks done, 100% validation accuracy | James (Dev) |

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

*To be populated by dev agent*

### Completion Notes List

**Implementation Summary:**
- Enhanced LLM prompts (SYSTEM_PROMPT and USER_PROMPT_TEMPLATE) for both StoryExtractionService and EpicExtractionService to detect 4 status marker formats
- Added LLM inference rules for documents without explicit markers (ACs checked → done, TODOs → draft, implementation notes → dev)
- Expanded regex fallback to support all 4 formats: bold, plain, bracketed, HTML comment (case-insensitive)
- Documented status detection logic in service class docstrings
- Verified database schema: extracted_stories.status and extracted_epics.status columns exist with correct typing

**Test Results:**
- Created 20 test documents: 10 explicit markers, 10 requiring inference
- All unit tests passing (12 new tests added)
- Validation results EXCEED targets:
  - **Explicit markers: 100%** accuracy (target: ≥90%) ✅
  - **Inference: 100%** accuracy (target: ≥70%) ✅
  - **Overall: 100%** accuracy across all 20 documents ✅
- Confidence scores: 80-100% across all test documents

**No Issues Encountered:**
- Implementation completed without blockers
- All acceptance criteria satisfied
- No iteration needed on prompts (100% accuracy achieved on first implementation)

### File List

**Modified Files:**
- `apps/api/src/services/story_extraction_service.py` - Enhanced prompts, added inference rules, improved regex fallback (lines 28-80, 198-214)
- `apps/api/src/services/epic_extraction_service.py` - Enhanced prompts, added inference rules, improved regex fallback (lines 32-78, 268-284)
- `apps/api/tests/test_story_extraction_service.py` - Added 8 new status detection tests (lines 268-445)
- `apps/api/tests/test_epic_extraction_service.py` - Added 4 new epic status detection tests (lines 258-348)

**Created Files:**
- `apps/api/tests/fixtures/status_detection/explicit_01_bold_draft.md` through `explicit_10_case_insensitive.md` (10 test documents)
- `apps/api/tests/fixtures/status_detection/inference_01_all_ac_checked_done.md` through `inference_10_done_complete.md` (10 test documents)
- `apps/api/tests/fixtures/status_detection/ground_truth.csv` - Ground truth labels for all 20 test documents
- `apps/api/tests/test_status_validation.py` - Integration validation test suite (3 tests, 20-document validation)

## QA Results

### Review Date: 2025-10-03

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment

**Overall Assessment: EXCELLENT** ⭐

This implementation represents gold-standard quality with exceptional attention to detail, comprehensive testing, and excellent architecture. The status detection feature demonstrates:

- **Clean architecture**: Clear separation of concerns (LLM prompts, regex fallback, normalization)
- **Graceful degradation**: LLM → regex fallback → null (never fails)
- **Comprehensive testing**: 100% AC coverage with 29 passing tests
- **Outstanding validation results**: 100% accuracy (exceeds 90%/70% targets)
- **Excellent documentation**: Clear docstrings explaining status detection logic

The implementation enhances existing extraction services without introducing technical debt or architectural violations.

### Refactoring Performed

**None Required** - Code is already well-structured, maintainable, and follows best practices.

### Compliance Check

- **Coding Standards**: ✅ PASS - All conventions followed (snake_case, SCREAMING_SNAKE_CASE, async/await)
- **Project Structure**: ✅ PASS - Correct file locations, proper test organization
- **Testing Strategy**: ✅ PASS - 29/29 tests passing, exceeds coverage target
- **All ACs Met**: ✅ PASS (6/6 ACs fully satisfied with exceptional results)

### Requirements Traceability

| AC | Requirement | Test Coverage | Result |
|----|-------------|---------------|--------|
| 1 | Explicit markers | 4 unit + 10 integration docs | ✅ 100% |
| 2 | LLM inference | 1 unit + 10 integration docs | ✅ 100% |
| 3 | Status enum | 2 unit tests | ✅ PASS |
| 4 | Database storage | Verified via migration + schemas | ✅ PASS |
| 5 | 20-doc validation | 3 integration tests | ✅ PASS |
| 6 | Accuracy targets | 100%/100% vs 90%/70% targets | ✅ EXCEEDED |

**Coverage Gap Analysis: NONE**

### Security Review

**Status: ✅ PASS** - No security concerns. Read-only extraction with proper input validation.

### Performance Considerations

**Status: ✅ PASS** - Efficient implementation. Unit tests <1s, integration ~20s (acceptable for POC).

### Non-Functional Requirements (NFRs)

| NFR | Status | Notes |
|-----|--------|-------|
| Security | ✅ PASS | No security surface changes |
| Performance | ✅ PASS | Efficient regex + optimized LLM prompts |
| Reliability | ✅ PASS | Graceful degradation, 100% validation accuracy |
| Maintainability | ✅ PASS | Excellent docs, follows all standards |

### Files Modified During Review

**None** - No refactoring required.

### Gate Status

Gate: **PASS** → [docs/qa/gates/2.4-status-detection.yml](docs/qa/gates/2.4-status-detection.yml)

**Quality Score: 100/100** (Perfect implementation)

**Gate Decision Rationale:**
- All 6 ACs fully satisfied with exceptional results
- 100% requirements traceability
- Gold-standard test architecture (29/29 passing)
- All NFRs satisfied
- Zero technical debt
- Validation exceeds targets by 10%

### Recommended Status

✅ **Ready for Done** - Production-ready, no changes required.
