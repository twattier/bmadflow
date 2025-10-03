# Epic 2 Accuracy Audit (Deferred from Story 2.6)

**Priority:** High
**Status:** Backlog
**Epic:** Epic 2: LLM-Powered Content Extraction
**Target Timeline:** Run in parallel with Epic 3 Week 1-2
**Effort:** ~4 hours

## Background

Epic 2 Story 2.6 delivered the validation tool but deferred the manual execution of 100-document accuracy validation. This audit is required to confirm that the extraction pipeline meets the 90%+ accuracy target stated in Epic 2 goals.

**Context from Epic 2 Retrospective:**
> **Issue:** Epic goal stated "90%+ extraction accuracy on 100-document validation set," but this was deferred.
>
> **Impact:**
> - Unknown actual extraction accuracy in production
> - Risk: Extraction may have systemic errors we haven't discovered
>
> **Recommendation:**
> - **Action:** Create backlog item for "Epic 2 Accuracy Audit"
> - **Owner:** PM/QA
> - **Timeline:** Before Epic 3 completion (parallel execution)
> - **Effort:** ~4 hours (2 hours ground truth creation, 1 hour validation run, 1 hour analysis)

## Objective

Validate that Epic 2 extraction pipeline achieves ≥90% accuracy on a 100-document test set, confirming Epic 2 success criteria are met.

## Tasks

### Task 1: Create Ground Truth Dataset (2 hours)
**Owner:** PM/QA

**Steps:**
1. Select 100 documents from bmad-flow project:
   - 50 epics (all available epic files)
   - 50 stories (representative sample across epics)
2. Manually review each document and create CSV ground truth file:
   - Column format: `document_id, expected_role, expected_action, expected_benefit, expected_status, expected_title, expected_goal`
   - For epics: focus on `expected_title`, `expected_goal`, `expected_status`
   - For stories: focus on `expected_role`, `expected_action`, `expected_benefit`, `expected_status`
3. Save as: `scripts/llm-evaluation/test_data/ground_truth_100_docs.csv`

### Task 2: Run Validation Tool (1 hour)
**Owner:** Dev/QA

**Steps:**
1. Ensure database has extracted data for all 100 documents
2. Run validation tool:
   ```bash
   cd /home/wsluser/dev/bmad-test/bmad-flow
   python scripts/validate_extraction.py \
     --project-id <project_uuid> \
     --ground-truth scripts/llm-evaluation/test_data/ground_truth_100_docs.csv \
     --output-report docs/validation-reports/epic-2-accuracy-audit.md
   ```
3. Review validation output for any errors

### Task 3: Analyze Results and Determine Actions (1 hour)
**Owner:** PM

**Steps:**
1. Review accuracy report (`docs/validation-reports/epic-2-accuracy-audit.md`)
2. Calculate overall accuracy and per-field accuracy:
   - Overall accuracy (all fields match): Target ≥90%
   - Role accuracy: Target ≥90%
   - Action accuracy: Target ≥85%
   - Status accuracy: Target ≥90%
   - Epic title accuracy: Target ≥95%
   - Epic goal accuracy: Target ≥85%
3. If accuracy <90%:
   - Analyze failure patterns (which types of documents fail? which fields?)
   - Prioritize: Activate Epic 2 Stories 2.7a (Prompt Engineering) and/or 2.7c (AC Parsing) as needed
   - Re-run validation after improvements
4. If accuracy ≥90%:
   - Mark Epic 2 as "Fully Validated"
   - Update Epic 2 status to include validation results
   - Close this backlog item

## Success Criteria

- [ ] 100-document ground truth dataset created
- [ ] Validation tool executed successfully
- [ ] Accuracy report generated
- [ ] Overall accuracy measured and documented
- [ ] If <90%: Improvement stories activated and re-validation scheduled
- [ ] If ≥90%: Epic 2 marked as "Fully Validated"

## Deliverables

1. `scripts/llm-evaluation/test_data/ground_truth_100_docs.csv` - Ground truth dataset
2. `docs/validation-reports/epic-2-accuracy-audit.md` - Accuracy report
3. Epic 2 epic file updated with validation results
4. Decision: Activate Stories 2.7a/2.7c or mark validation complete

## Dependencies

- ✅ Epic 2 Story 2.6: Validation tool implemented
- ✅ Epic 2 Story 2.5: Extraction pipeline populated database
- Project synced with sufficient documents for validation

## Risks

| Risk | Mitigation |
|------|------------|
| Accuracy <90% requires rework | Time-boxed: If Stories 2.7a/2.7c activated, limit to 1 day total |
| Ground truth creation subjective | Have 2 people review edge cases, document ambiguous decisions |
| Database doesn't have all documents | Run sync before validation to ensure full dataset |

## Timeline

- **Ideal Start:** Epic 3 Week 1 (Day 1-2)
- **Parallel with:** Epic 3 Stories 3.1-3.2 implementation
- **Completion Target:** Before Epic 3 Week 2 begins
- **Total Duration:** 1-2 days (depends on whether improvements needed)

## Owner

**Primary:** PM (coordinates, analyzes results)
**Support:** QA (creates ground truth), Dev (runs tool, implements improvements if needed)

---

**Backlog Item Created:** 2025-10-03
**Created By:** Claude (PM)
**Linked Epic:** [Epic 2: LLM-Powered Content Extraction](../epics/epic-2-llm-content-extraction.md)
**Linked Retrospective:** [Epic 2 Retrospective](../retrospectives/epic-2-retrospective.md)
