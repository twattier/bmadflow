# Technical Debt: LLM Provider Evaluation Documentation

**ID:** TECH-DEBT-2
**Epic:** Epic 1 (Foundation)
**Priority:** Medium
**Created:** 2025-10-02
**Status:** ✅ Resolved (Retroactive Documentation)
**Resolved:** 2025-10-03

## Issue Description

Story 1.7 (LLM Provider Selection) acceptance criteria require comprehensive evaluation documentation that is currently missing:

**Missing Artifacts:**
1. `docs/llm-provider-evaluation.md` file with evaluation results
2. Evaluation script in `scripts/llm-evaluation/` directory
3. Test dataset (20 BMAD sample documents: 10 epics + 10 stories)
4. Documented evaluation metrics (accuracy, latency, cost, embedding compatibility)

**What Exists:**
- README documents final selection: OLLAMA (local) with qwen2.5:3b
- Rationale provided: Privacy (40% weight), zero cost, sufficient for POC
- Embedding dimension compatibility warning documented

## Impact

- **Audit Trail Missing:** No record of why OLLAMA was chosen over LiteLLM proxy
- **Decision Validation Risk:** Cannot verify if selection criteria were actually measured
- **Future Reevaluation Risk:** No baseline metrics for comparing if provider needs to change
- **Compliance Risk:** Missing evidence for technical decision-making process

## Root Cause

Likely one of:
1. Evaluation done informally without documentation
2. Provider selected based on constraints (privacy, cost) without formal testing
3. Story AC created after provider selection was already made

## Recommended Solution

**Retroactive Documentation (Lightweight)**
1. Create `docs/llm-provider-evaluation.md` with:
   - Provider options considered (OLLAMA local, LiteLLM proxy)
   - Selection criteria and weights (privacy 40%, capability 30%, cost 20%, latency 10%)
   - Rationale for OLLAMA selection
   - Known trade-offs and limitations
   - Embedding dimension decision
2. Document "evaluation method: constraint-based selection" (vs formal testing)
3. Mark formal testing as "deferred to post-POC phase"

**OR Full Evaluation (If Time Permits)**
1. Create test dataset: 20 BMAD sample docs from `github.com/bmad-code-org/BMAD-METHOD`
2. Build evaluation script in `scripts/llm-evaluation/`
3. Run extraction tests with both providers
4. Measure accuracy, latency, cost
5. Document results in `docs/llm-provider-evaluation.md`

## Acceptance Criteria

**Minimum (Retroactive Doc):**
- [x] `docs/llm-provider-evaluation.md` file created
- [x] Provider options documented with selection rationale
- [x] Trade-offs and limitations explicitly stated
- [x] Embedding dimension decision documented
- [x] Story 1.7 marked as "documented retroactively"

**Ideal (Full Evaluation):**
- [ ] Test dataset created (20 BMAD docs)
- [ ] Evaluation script in `scripts/llm-evaluation/`
- [ ] Extraction accuracy measured for both providers
- [ ] Latency and cost metrics documented
- [ ] Results table in evaluation doc

## Related Items

- Epic 1, Story 1.7: LLM Provider Selection and Validation
- Epic 2, Story 2.2: Will use selected LLM provider

## Effort Estimate

- **Retroactive Doc:** 1-2 hours
- **Full Evaluation:** 8-12 hours

## Notes

- Not blocking for Epic 2 (provider already selected and working)
- Useful for future provider reevaluation if OLLAMA proves insufficient
- Could be combined with Epic 2 work (create evaluation framework while building extraction)
