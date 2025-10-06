# Story Review Checklist

**Purpose:** Ensure documentation consistency before marking stories as "Done"

**When to use:** Before approving any story or at the end of each development cycle

---

## Pre-Review Checklist (Developer)

Before moving a story to "Review" status, verify:

### ✅ Story File Completeness

- [ ] **Status Field** is set to "Review"
- [ ] **Story ID** follows format: `{Epic}.{Story}` (e.g., 1.3)
- [ ] **Title** is clear and descriptive
- [ ] **Acceptance Criteria** are numbered and testable
- [ ] **All Acceptance Criteria** are marked as complete (or blocked with explanation)

### ✅ Implementation Documentation

- [ ] **File List** section exists and is complete
  - [ ] All created files are listed with descriptions
  - [ ] All modified files are listed with change descriptions
  - [ ] No files are missing from the list
- [ ] **Implementation Notes** section exists and describes:
  - [ ] What was built
  - [ ] How it works
  - [ ] Any deviations from the original plan
  - [ ] Any design decisions made during implementation

### ✅ Testing Coverage

- [ ] All tests are passing (unit, integration, e2e as applicable)
- [ ] **Testing Notes** section exists (if tests were added)
- [ ] Test files are included in File List

### ✅ Related Documentation

- [ ] Architecture docs updated (if new patterns introduced)
  - [ ] Changes documented in relevant [docs/architecture/](architecture/) files
  - [ ] Architecture docs added to story File List
- [ ] Context docs updated (if external patterns changed)
  - [ ] Changes documented in [docs/context/](context/) files via MCP
  - [ ] Context docs added to story File List

---

## QA Review Checklist (Test Architect)

Run this checklist during `/BMad/tasks/review-story`:

### ✅ Story Validation

- [ ] Story file exists in `docs/stories/`
- [ ] Status is "Review" (not "In Progress" or other)
- [ ] All required sections are present
- [ ] Acceptance criteria are clear and testable

### ✅ Implementation Validation

- [ ] **File List is accurate**
  - [ ] Run `git diff` to verify all changed files are listed
  - [ ] Check that descriptions match actual changes
- [ ] **Implementation Notes are complete**
  - [ ] Clear explanation of what was built
  - [ ] Design decisions are documented
- [ ] **Code quality meets standards**
  - [ ] Follows [docs/architecture/coding-standards.md](architecture/coding-standards.md)
  - [ ] No obvious technical debt introduced
  - [ ] Proper error handling in place

### ✅ Testing Validation

- [ ] All tests pass (run test suite)
- [ ] Test coverage is adequate
  - [ ] Backend: 70%+ coverage (see [NFR18](prd.md))
  - [ ] Frontend: 60%+ coverage
  - [ ] Critical paths have E2E tests
- [ ] Test quality is good
  - [ ] Tests are maintainable
  - [ ] Tests follow AAA pattern (Arrange-Act-Assert)
  - [ ] Tests have clear names and descriptions

### ✅ Architecture Compliance

- [ ] Follows project structure defined in [docs/architecture/source-tree.md](architecture/source-tree.md)
- [ ] Uses patterns from [docs/context/](context/) correctly
- [ ] Adheres to [docs/architecture/coding-standards.md](architecture/coding-standards.md)
- [ ] Error handling follows [docs/architecture/error-handling.md](architecture/error-handling.md)

### ✅ Documentation Updates

- [ ] Architecture docs are up to date
  - [ ] New patterns documented
  - [ ] Changes reflected in relevant files
- [ ] Context docs are current
  - [ ] External patterns updated via MCP
  - [ ] No outdated patterns referenced
- [ ] API documentation updated (if API changed)
  - [ ] OpenAPI/Swagger specs current
  - [ ] Endpoint descriptions accurate

### ✅ Security & Performance

- [ ] No security vulnerabilities introduced
  - [ ] No hardcoded credentials
  - [ ] Proper input validation
  - [ ] Authentication/authorization in place
- [ ] Performance requirements met
  - [ ] API response times acceptable
  - [ ] No obvious performance issues
  - [ ] Database queries optimized

### ✅ Quality Gate

- [ ] **QA Results** section added to story file
- [ ] **Quality gate file** created in `docs/qa/gates/`
  - [ ] File naming: `{epic}.{story}-{slug}.yml`
  - [ ] Gate status determined: PASS/CONCERNS/FAIL/WAIVED
  - [ ] All sections completed
- [ ] **Recommended status** provided to developer

---

## Post-Review Checklist (Developer)

After QA review, before marking "Done":

### ✅ Address Review Findings

- [ ] All issues from QA Results addressed
- [ ] All unchecked items from Improvements Checklist completed
- [ ] Any refactoring suggestions implemented (if applicable)

### ✅ Final Documentation

- [ ] Review QA Results section in story file
- [ ] Verify quality gate file exists
- [ ] Update File List if new files added during fixes
- [ ] Confirm gate status is PASS or acceptable CONCERNS

### ✅ Status Update

- [ ] Update story Status to "Done" (only if gate is PASS or accepted CONCERNS)
- [ ] Add completion date to story file
- [ ] Link to quality gate file in story

---

## Weekly Documentation Audit

Run these checks at the end of each week:

### ✅ Story Status Consistency

```bash
# Check for stories in "Done" without gate files
for story in docs/stories/*.md; do
  if grep -q "^Status: Done" "$story"; then
    story_id=$(grep "^Story ID:" "$story" | cut -d: -f2 | tr -d ' ')
    if [ ! -f "docs/qa/gates/${story_id}"*.yml ]; then
      echo "⚠️  Missing gate for Done story: $story"
    fi
  fi
done
```

### ✅ File List Accuracy

```bash
# Check for stories in "Review" with empty File List
for story in docs/stories/*.md; do
  if grep -q "^Status: Review" "$story"; then
    if ! grep -q "## File List" "$story"; then
      echo "⚠️  Missing File List in Review story: $story"
    fi
  fi
done
```

### ✅ Documentation Coverage

```bash
# Generate coverage report
echo "📊 Documentation Status Report"
echo "=============================="
echo "Total stories: $(ls docs/stories/*.md 2>/dev/null | wc -l)"
echo "Stories with gates: $(ls docs/qa/gates/*.yml 2>/dev/null | wc -l)"
echo ""
echo "Status distribution:"
grep -h "^Status:" docs/stories/*.md 2>/dev/null | sort | uniq -c
```

---

## Common Issues and Solutions

### Issue 1: Story marked "Review" with incomplete File List

**Symptoms:**
- File List is missing
- File List doesn't include all changes
- Git diff shows files not in File List

**Solution:**
```bash
1. Review git diff to find all changed files
2. Add missing files to File List with descriptions
3. Update Implementation Notes to reflect all changes
4. Keep status as "Review" and request re-review
```

### Issue 2: Story marked "Done" without QA Results

**Symptoms:**
- No "## QA Results" section
- No quality gate file in docs/qa/gates/

**Solution:**
```bash
1. Revert Status to "Review"
2. Run /BMad/tasks/review-story command
3. Wait for QA to complete review
4. Address any issues found
5. Update to "Done" only after QA approval
```

### Issue 3: Tests failing but story in "Review"

**Symptoms:**
- CI/CD pipeline fails
- Test suite has failures
- Story status is "Review"

**Solution:**
```bash
1. Revert Status to "In Progress"
2. Fix failing tests
3. Update File List with any new test files
4. Verify all tests pass
5. Move back to "Review"
```

### Issue 4: Architecture changed but docs not updated

**Symptoms:**
- Code uses new patterns
- Architecture docs don't reflect changes
- Story doesn't mention architecture updates

**Solution:**
```bash
1. Identify which architecture doc needs updating
2. Update the relevant docs/architecture/*.md file
3. Add architecture doc to story File List
4. Add note in Implementation Notes about pattern change
5. Request re-review
```

### Issue 5: Context docs outdated

**Symptoms:**
- External library updated
- Patterns in context docs don't match library version
- Code doesn't follow context doc patterns

**Solution:**
```bash
1. Use MCP to fetch latest library docs:
   mcp__context7__get-library-docs("{library}")
2. Update relevant docs/context/*/*.md file
3. Update code to follow new patterns
4. Add context doc to story File List
5. Note pattern update in Implementation Notes
```

---

## Escalation Path

If any of these conditions are met, escalate to team lead:

- [ ] Critical security issues found
- [ ] Major architecture violations
- [ ] Tests cannot be made to pass
- [ ] Requirements unclear or contradictory
- [ ] External dependency blocking progress
- [ ] Technical debt too high to accept

---

## Automation Support

### Git Pre-Commit Hook

The pre-commit hook automatically checks:
- Story file completeness
- File List presence for stories in "Review"
- Status field validity

Location: `.git/hooks/pre-commit` (created by setup script)

### Review Command

The `/BMad/tasks/review-story` command automates:
- Story validation
- File List verification
- QA Results creation
- Quality gate file generation

---

## Metrics to Track

Track these metrics monthly:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Stories with complete File Lists | 100% | Count stories in "Review"/"Done" with File List |
| Stories with QA Results | 100% of "Done" stories | Count "Done" stories with QA Results section |
| Quality gate files | 100% of "Done" stories | Count gate files vs "Done" stories |
| Documentation lag | < 1 day | Time between code complete and docs updated |
| Review rework rate | < 20% | Stories requiring changes after review |

---

## Best Practices

1. **Update docs as you code**, don't wait until the end
2. **Review your own work** before moving to "Review" status
3. **Be specific** in Implementation Notes and File List descriptions
4. **Link related docs** when documenting pattern changes
5. **Ask for help** if requirements or patterns are unclear
6. **Keep commits atomic** with related doc updates in same commit

---

## Related Documentation

- [DOCUMENTATION-CONSISTENCY-RULES.md](DOCUMENTATION-CONSISTENCY-RULES.md) - Global rules
- [DOCUMENTATION-MAP.md](DOCUMENTATION-MAP.md) - Documentation hierarchy
- [development-workflow.md](architecture/development-workflow.md) - Development process
- [code-examples-policy.md](architecture/code-examples-policy.md) - Code standards

---

**Remember: This checklist ensures our documentation always reflects reality. Take the time to do it right!**
