# Documentation Consistency System - Setup Complete

**Date:** 2025-10-06
**Status:** ✅ Complete

---

## What Was Implemented

A comprehensive documentation consistency system to ensure the [docs/](docs/) folder always reflects the current state of the codebase.

### Core Principle

> **When a developer says "it's on review", the story file MUST be updated with accurate, consistent information that matches the actual implementation.**

---

## Key Components

### 1. Documentation Consistency Rules
**File:** [DOCUMENTATION-CONSISTENCY-RULES.md](DOCUMENTATION-CONSISTENCY-RULES.md)

Defines global rules for keeping documentation in sync with code:
- Story status transitions require documentation updates
- Code changes must update relevant docs
- Story files must be complete before "Review" status
- Documentation hierarchy and authority
- Quality gate requirements

### 2. Review Checklist
**File:** [REVIEW-CHECKLIST.md](REVIEW-CHECKLIST.md)

Manual checklist for ensuring documentation completeness:
- Pre-review checklist for developers
- QA review validation steps
- Post-review tasks
- Weekly audit procedures
- Common issues and solutions

### 3. Pre-Commit Hook (Automated)
**File:** [.git/hooks/pre-commit](.git/hooks/pre-commit)

Automatically validates before each commit:
- Story files have Status field
- Stories in "Review" have File List
- Stories in "Done" have QA Results
- Stories in "Done" have quality gate files
- Warns if code changes aren't in any story File List

### 4. Audit Scripts
**Location:** [docs/scripts/](scripts/)

Utility scripts for weekly documentation audits:

- **check-story-gates.sh** - Verify Done stories have quality gate files
- **check-file-lists.sh** - Verify Review stories have File Lists
- **doc-coverage-report.sh** - Generate comprehensive coverage report
- **README.md** - Script documentation

### 5. Updated Development Workflow
**File:** [docs/architecture/development-workflow.md](architecture/development-workflow.md)

Added comprehensive "Documentation Requirements" section:
- Story status workflow
- Pre-commit hook usage
- Documentation update guidelines
- Commit message format with story references
- Weekly audit procedures

### 6. Updated Documentation Map
**File:** [DOCUMENTATION-MAP.md](DOCUMENTATION-MAP.md)

Updated with:
- Rule 0: Documentation Must Always Be Current
- New mandatory docs added to Quick Links
- Scripts added to Common Tasks
- Documentation consistency in Learning Path

---

## How It Works

### For Developers

#### During Development
1. **Update story File List** as you create/modify files
2. **Add Implementation Notes** describing what you're building
3. **Update architecture docs** if patterns change
4. **Update context docs** if external patterns change (via MCP)

#### Before Moving to "Review"
```bash
# 1. Ensure story file is complete
# - All ACs implemented
# - File List complete
# - Implementation Notes written
# - All tests passing

# 2. Update story status
# Status: In Progress → Review

# 3. Commit with story reference
git add .
git commit -m "feat(story-1.3): implement feature

- Implementation complete
- Updated story File List and Implementation Notes

Story: 1.3
Status: Review"

# Pre-commit hook runs automatically and validates!
```

### For QA

#### Review Process
```bash
# 1. Run review command
/BMad/tasks/review-story

# 2. This automatically:
# - Validates story completeness
# - Checks File List accuracy
# - Adds QA Results section
# - Creates quality gate file
# - Recommends status change
```

### Weekly Audits

#### Run These Scripts Every Week
```bash
# Generate overview report
./docs/scripts/doc-coverage-report.sh

# Check for missing gate files
./docs/scripts/check-story-gates.sh

# Check for missing File Lists
./docs/scripts/check-file-lists.sh
```

---

## Enforcement Mechanisms

### 1. Automated (Pre-Commit Hook)
✅ Runs automatically on every commit
✅ Validates story completeness
✅ Prevents commits with incomplete documentation
✅ Can be bypassed with `--no-verify` (not recommended)

### 2. Manual (Review Checklist)
✅ Used during QA review
✅ Ensures all requirements met
✅ Verifies File List accuracy
✅ Confirms quality gate creation

### 3. Weekly (Audit Scripts)
✅ Generates coverage reports
✅ Identifies missing gate files
✅ Finds incomplete File Lists
✅ Tracks documentation metrics

---

## Story File Template

Every story should follow this structure:

```markdown
# Story {Epic}.{Story}: {Title}

**Status:** Draft
**Epic:** {Epic Number}
**Story Points:** {1-13}
**Priority:** High/Medium/Low

## Acceptance Criteria

1. [Clear, testable criterion]
2. [Clear, testable criterion]
3. [Clear, testable criterion]

## Dependencies

- Story {X}.{Y} must be complete

## Technical Notes

[Design decisions, approach, constraints]

## Implementation Notes

[What was built, how it works, any deviations from plan]

## File List

### Created
- `path/to/new/file.ts` - Description

### Modified
- `path/to/existing/file.ts` - Description of changes

## Testing Notes

[Test strategy, coverage, any test-specific details]

## QA Results

[Appended by QA during review - DO NOT edit manually]
```

---

## Git Integration

### Pre-Commit Hook Location
```
.git/hooks/pre-commit
```

### Commit Message Format
```
<type>(story-{epic}.{story}): <subject>

<body>

Story: {epic}.{story}
Status: {current_status}
```

### Example
```
feat(story-1.3): implement user authentication

- Added JWT token generation
- Implemented login/logout endpoints
- Updated story 1.3 File List and Implementation Notes

Story: 1.3
Status: Review
```

---

## Quality Gates

Every story marked "Done" requires a quality gate file in `docs/qa/gates/`.

### Gate File Naming
```
{epic}.{story}-{slug}.yml
```

### Gate Statuses
- **PASS**: All critical requirements met, ready for production
- **CONCERNS**: Non-critical issues, team should review
- **FAIL**: Critical issues that must be addressed
- **WAIVED**: Issues acknowledged but explicitly waived

Gate files are created automatically by `/BMad/tasks/review-story` command.

---

## Files Created/Modified

### New Files Created
- [docs/DOCUMENTATION-CONSISTENCY-RULES.md](DOCUMENTATION-CONSISTENCY-RULES.md)
- [docs/REVIEW-CHECKLIST.md](REVIEW-CHECKLIST.md)
- [docs/SETUP-DOCUMENTATION-SYSTEM.md](SETUP-DOCUMENTATION-SYSTEM.md) (this file)
- [.git/hooks/pre-commit](.git/hooks/pre-commit)
- [docs/scripts/check-story-gates.sh](scripts/check-story-gates.sh)
- [docs/scripts/check-file-lists.sh](scripts/check-file-lists.sh)
- [docs/scripts/doc-coverage-report.sh](scripts/doc-coverage-report.sh)
- [docs/scripts/README.md](scripts/README.md)

### Modified Files
- [docs/architecture/development-workflow.md](architecture/development-workflow.md)
  - Added "Documentation Requirements" section
- [docs/DOCUMENTATION-MAP.md](DOCUMENTATION-MAP.md)
  - Added Rule 0: Documentation Must Always Be Current
  - Updated Quick Links with new mandatory docs
  - Added scripts to Common Tasks
  - Updated Learning Path

---

## Next Steps

### For Team
1. **Read** [DOCUMENTATION-CONSISTENCY-RULES.md](DOCUMENTATION-CONSISTENCY-RULES.md) - **MANDATORY**
2. **Read** [REVIEW-CHECKLIST.md](REVIEW-CHECKLIST.md) - **MANDATORY**
3. **Test** the pre-commit hook by making a commit
4. **Run** weekly audit scripts to establish baseline metrics
5. **Follow** the story workflow for all future development

### For Scrum Master
1. Schedule weekly documentation audits
2. Track compliance metrics
3. Ensure team follows rules
4. Address violations promptly

### For QA
1. Use `/BMad/tasks/review-story` for all reviews
2. Ensure quality gate files are created
3. Verify File List accuracy during review
4. Recommend status changes based on gate results

---

## Measurement & Success Criteria

### Weekly Metrics to Track

| Metric | Target | Script |
|--------|--------|--------|
| Stories with complete File Lists | 100% | check-file-lists.sh |
| Stories with quality gates | 100% of "Done" | check-story-gates.sh |
| Documentation coverage | 100% | doc-coverage-report.sh |
| Review rework rate | < 20% | Manual tracking |

### Success Indicators
- ✅ All "Done" stories have quality gate files
- ✅ All "Review" stories have complete File Lists
- ✅ Pre-commit hook prevents incomplete documentation
- ✅ Weekly audits show 100% compliance
- ✅ Team follows documentation workflow naturally

---

## Troubleshooting

### Pre-Commit Hook Not Running
```bash
# Ensure hook is executable
chmod +x .git/hooks/pre-commit

# Test hook manually
.git/hooks/pre-commit
```

### Script Permission Errors
```bash
# Make all scripts executable
chmod +x docs/scripts/*.sh
```

### Missing Quality Gate Files
```bash
# Run check script
./docs/scripts/check-story-gates.sh

# Create missing gates using review command
/BMad/tasks/review-story
```

### Empty File Lists
```bash
# Run check script
./docs/scripts/check-file-lists.sh

# Update story files manually
# See DOCUMENTATION-CONSISTENCY-RULES.md for guidance
```

---

## Related Documentation

- [DOCUMENTATION-CONSISTENCY-RULES.md](DOCUMENTATION-CONSISTENCY-RULES.md) - 🚨 **MANDATORY** - Global rules
- [REVIEW-CHECKLIST.md](REVIEW-CHECKLIST.md) - 🚨 **MANDATORY** - Review checklist
- [DOCUMENTATION-MAP.md](DOCUMENTATION-MAP.md) - Documentation hierarchy
- [architecture/development-workflow.md](architecture/development-workflow.md) - Development process
- [scripts/README.md](scripts/README.md) - Audit scripts documentation

---

**The documentation consistency system is now active and ready to use!** 🎉

Remember: **Documentation is not an afterthought. It's a first-class citizen that must always reflect reality.**
