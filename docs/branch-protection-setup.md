# GitHub Branch Protection Setup Guide

**Status:** ⚠️ NOT CONFIGURED - Requires Repository Admin Action
**Priority:** Medium (Low for single developer, HIGH when team grows)
**Time Required:** 5 minutes

---

## Why This Matters

Without branch protection:
- ❌ Failing CI tests can be bypassed
- ❌ Code can be pushed directly to `main` without review
- ❌ Broken builds can land in main branch

**Current State:** CI/CD pipeline runs but doesn't block merges

---

## Setup Instructions

### Prerequisites
- Must have **Admin access** to repository
- Repository: `github.com/twattier/bmadflow` (or your fork)

### Steps

1. **Navigate to Repository Settings**
   - Go to repository on GitHub
   - Click **Settings** tab (top right)
   - Click **Branches** in left sidebar

2. **Add Branch Protection Rule**
   - Click **"Add branch protection rule"**
   - **Branch name pattern:** `main`

3. **Configure Required Settings**
   Check these boxes:

   ✅ **Require status checks to pass before merging**
   - Select status checks:
     - ✅ `backend-ci`
     - ✅ `frontend-ci`

   ✅ **Require branches to be up to date before merging**
   - Ensures PR includes latest main before merge

   ✅ **Require a pull request before merging** (RECOMMENDED)
   - Prevents direct pushes to main
   - Recommended even for single developer (enforces review workflow)

   ⚠️ **Optional but recommended:**
   - ✅ Require conversation resolution before merging
   - ✅ Require linear history
   - ✅ Do not allow bypassing the above settings

4. **Save Changes**
   - Scroll to bottom
   - Click **"Create"** or **"Save changes"**

---

## Verification

### Test 1: Failing CI Blocks Merge

```bash
# Create test branch
git checkout -b test-branch-protection

# Add failing test
echo "assert False, 'Intentional failure for testing'" >> apps/api/tests/test_health.py

# Commit and push
git add apps/api/tests/test_health.py
git commit -m "test: Add failing test to verify branch protection"
git push origin test-branch-protection

# Create PR on GitHub
# Expected: CI fails, merge button shows "Checks must pass"
# Expected: Merge button is DISABLED
```

**Cleanup:**
```bash
git checkout main
git branch -D test-branch-protection
git push origin --delete test-branch-protection
```

### Test 2: Direct Push to Main Blocked

```bash
# Try to push directly to main
git checkout main
echo "# Test" >> README.md
git add README.md
git commit -m "test: Direct push attempt"
git push origin main

# Expected: Push REJECTED with message about branch protection
# If successful: Branch protection not configured correctly
```

**Cleanup:**
```bash
git reset --hard HEAD~1  # Undo commit
```

---

## Configuration Summary

Once configured, the following workflow is enforced:

1. ✅ All changes must go through Pull Requests
2. ✅ CI must pass (backend-ci + frontend-ci) before merge
3. ✅ Branch must be up to date with main
4. ✅ Direct pushes to main are blocked

---

## Troubleshooting

### "Status checks not found"
**Problem:** CI hasn't run yet on a PR
**Solution:**
- Push a commit to trigger CI
- Check `.github/workflows/ci.yml` job names match exactly: `backend-ci`, `frontend-ci`

### "I can still push to main"
**Problem:** Branch protection not applied or you have admin override
**Solution:**
- Verify branch name pattern is exactly `main` (case-sensitive)
- Check "Do not allow bypassing" is enabled
- Admins can bypass by default unless explicitly disabled

### "CI passes but merge still blocked"
**Problem:** Branch not up to date with main
**Solution:**
- Merge main into your branch: `git merge origin/main`
- Or rebase: `git rebase origin/main`
- Push updated branch

---

## Status Check

After setup, verify in repository settings:

```
Settings > Branches > Branch protection rules
Should show:
  main
    - Require status checks: backend-ci, frontend-ci
    - Require up to date branch
    - Require pull request
```

---

## Notes

- **Not automatable:** GitHub doesn't support branch protection in `.github/` files
- **Per-repository:** Must configure for each fork/copy
- **Admin-only:** Regular contributors cannot configure this
- **Team growth:** Increase priority to HIGH when adding 2nd developer

---

## Related

- CI/CD Pipeline: `.github/workflows/ci.yml`
- Epic 1, Story 1.8: CI/CD Pipeline Setup
- Technical Debt: TECH-DEBT-3

