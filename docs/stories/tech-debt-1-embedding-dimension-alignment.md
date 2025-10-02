# Technical Debt: Embedding Dimension Alignment

**ID:** TECH-DEBT-1
**Epic:** Epic 1 (Foundation)
**Priority:** Medium
**Created:** 2025-10-02
**Status:** Open

## Issue Description

There is a discrepancy between the database schema and documentation regarding vector embedding dimensions:

- **Database Schema** (`alembic/versions/202510020046_initial_schema...py:52`): Defines `embedding` column as `Vector(384)`
- **README Documentation** (line 123): States OLLAMA uses `nomic-embed-text` with **768-dimensional embeddings**

## Impact

- **Data Compatibility Risk:** If embeddings are generated using 768d model but stored in 384d schema, data truncation or errors will occur
- **Provider Lock-in Risk:** README warns "Embedding dimension locked" but actual dimension unclear
- **Future Migration Risk:** Cannot switch embedding models without understanding actual dimension used

## Root Cause

Likely caused by one of:
1. Schema created before final LLM provider selection
2. Documentation updated but schema not migrated
3. Different models evaluated (384d vs 768d)

## Recommended Solution

**Option 1: Align to 768d (Recommended)**
1. Verify actual OLLAMA `nomic-embed-text` output dimension
2. Create Alembic migration to alter column: `ALTER TABLE documents ALTER COLUMN embedding TYPE vector(768)`
3. Confirm no existing embeddings in database (POC phase)
4. Update documentation if dimension is actually 384d

**Option 2: Align to 384d**
1. Verify if 384d model is actually being used
2. Update README to reflect correct model and dimension
3. Document why 384d was chosen over 768d

## Acceptance Criteria

- [ ] Actual embedding dimension verified via OLLAMA API call
- [ ] Database schema matches documented dimension
- [ ] README accurately reflects embedding model and dimension
- [ ] Migration script created (if schema change needed)
- [ ] Test confirms embeddings can be stored and retrieved
- [ ] Documentation updated with rationale for dimension choice

## Related Items

- Epic 1, Story 1.2: Database Schema for Documents
- Epic 1, Story 1.7: LLM Provider Selection and Validation

## Effort Estimate

**2-4 hours** (investigation + migration + testing)

## Notes

- Must be resolved before Epic 2 Story 2.2 (LLM extraction with embeddings)
- Zero data loss risk in POC phase (no production data)
- Decision impacts storage requirements (768d = 2x storage of 384d)
