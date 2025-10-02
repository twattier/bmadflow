# Technical Debt: GitHub Branch Protection Configuration

**ID:** TECH-DEBT-3
**Epic:** Epic 1 (Foundation)
**Priority:** Medium
**Created:** 2025-10-02
**Status:** Open

## Issue Description

Story 1.8 (CI/CD Pipeline Setup) acceptance criterion #6 requires test failures to prevent PR merge, but GitHub branch protection rules are **not currently configured**.

**Current State:**
- CI/CD pipeline exists and runs (`.github/workflows/ci.yml`)
- Both `backend-ci` and `frontend-ci` jobs execute on PRs
- README includes manual setup instructions (lines 165-174)
- ✅ Build status badge visible in README

**Missing:**
- Branch protection rules not enabled on `main` branch
- Required status checks not enforced
- PRs can be merged even if CI fails

## Impact

- **Code Quality Risk:** Failing tests can be bypassed by merging without CI passing
- **Broken Main Risk:** Commits that break build can be pushed directly to `main`
- **Team Workflow Risk:** No enforcement of "branches must be up to date" requirement
- **Low Severity:** Only 1 developer currently, but risky for team growth

## Root Cause

Branch protection requires **repository admin privileges** to configure. Cannot be automated via code, must be done manually in GitHub UI.

## Recommended Solution

**Manual Configuration Task (5 minutes)**

Repository administrator must:

1. Navigate to: **Repository Settings** → **Branches**
2. Click **"Add branch protection rule"**
3. Branch name pattern: `main`
4. Enable settings:
   - ✅ **"Require status checks to pass before merging"**
   - ✅ **"Require branches to be up to date before merging"**
   - Select required checks:
     - ✅ `backend-ci`
     - ✅ `frontend-ci`
   - ✅ **"Require a pull request before merging"** (optional, best practice)
   - ✅ **"Require conversation resolution before merging"** (optional)
5. Click **"Create"** or **"Save changes"**

## Acceptance Criteria

- [ ] Branch protection rule created for `main` branch
- [ ] Required status checks configured: `backend-ci` and `frontend-ci`
- [ ] "Require branches to be up to date" enabled
- [ ] Test: Create PR with failing test, verify merge button is blocked
- [ ] Test: Push directly to main with failing test, verify push is rejected
- [ ] Document configuration in README or team wiki

## Related Items

- Epic 1, Story 1.8: CI/CD Pipeline Setup

## Effort Estimate

**5 minutes** (manual configuration only)

## Notes

- **Prerequisite:** Must have GitHub repository admin access
- **Who can do it:** Repository owner or users with admin role
- Not automatable via Infrastructure-as-Code (GitHub doesn't support branch protection in `.github/` files)
- Consider adding to project onboarding checklist for future repositories
- Low priority if single developer, **increase to HIGH** when team grows to 2+ developers

## Verification Steps

After configuration, test with:
```bash
# Create test branch with intentional failure
git checkout -b test-branch-protection
# Edit test file to cause failure
# Commit and push
git push origin test-branch-protection
# Create PR
# Verify: GitHub shows "Some checks were not successful" and merge is blocked
```
