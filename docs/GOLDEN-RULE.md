# 🚨 GOLDEN RULE: Keep Documentation Current

---

## The Rule

> **The [docs/](docs/) folder should reflect the current state of the project.**

**If you change something important, update the docs.**

---

## Why This Matters

- ✅ **Trust** - Team can rely on docs to be accurate
- ✅ **Velocity** - No time wasted on outdated information
- ✅ **Onboarding** - New team members get current information

---

## What to Update

### Core Documentation (Keep These Current)

**When requirements change:**
- Update [docs/prd.md](prd.md)

**When architecture/design changes:**
- Update relevant [docs/architecture/](architecture/) files

**When setup/deployment changes:**
- Update README.md
- Update [docs/architecture/deployment.md](architecture/deployment.md)

### During Development (Story Work)

**As you implement:**
- Add notes in story Implementation Notes
- List modified files in story File List
- Document any architectural decisions made

---

## Common Sense Guidelines

### ✅ DO Update Docs When:
- API endpoints change significantly
- Database schema changes (migrations are auto-documented)
- Core tech stack changes (major version upgrades)
- Architecture patterns change
- Requirements are clarified or modified

### ⚠️ DON'T Obsess Over:
- Every minor code change
- Refactoring that doesn't change behavior
- Temporary implementation details
- Internal helper functions

---

## For POC/MVP Projects

This is a **Proof of Concept** with 3 users and local deployment.

**Focus on:**
- ✅ Keeping PRD and Architecture docs roughly current
- ✅ README has accurate setup instructions
- ✅ Major decisions are captured somewhere

**Don't worry about:**
- ❌ Perfect documentation coverage
- ❌ Detailed handoff materials
- ❌ Comprehensive user guides
- ❌ Weekly audits and compliance checks

---

## Quick Examples

### ✅ GOOD: Update When It Matters

```markdown
Developer: I changed the database from SQLite to PostgreSQL
Action: Update architecture/database-schema.md and tech-stack.md
Reason: This is a significant architectural change
```

### ✅ ALSO GOOD: Skip When It Doesn't

```markdown
Developer: I refactored the sync function into smaller helpers
Action: Just commit the code with good commit message
Reason: Internal refactoring, no external impact
```

---

## Remember

**Documentation helps the team. Keep the important stuff current, but don't let documentation slow you down.**

**For a POC: Focus on README, PRD, and Architecture docs. Everything else is nice-to-have.**

---
