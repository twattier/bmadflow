# How to Use docs/context/

> **Quick Reference**: This directory contains **external library documentation** populated by MCP services. NOT BMADFlow-specific code.

---

## 🎯 What is docs/context/?

**Purpose**: Downloaded official documentation from libraries we use frequently

**Source**: Populated by **MCP services** (context7, shadcn)

**Contains**:
- ✅ FastAPI async patterns, dependency injection, Pydantic models
- ✅ shadcn/ui component examples (Table, Card, Form, Dialog)
- ✅ PostgreSQL + pgvector patterns (vector columns, similarity search, HNSW)
- ✅ Docker Compose orchestration patterns

**Does NOT Contain**:
- ❌ BMADFlow business logic
- ❌ Application-specific implementations
- ❌ Custom project code

---

## 📖 Quick Start

### Step 1: Read Context Docs Before Implementing

```bash
# Implementing backend API endpoint?
cat docs/context/backend/fastapi-patterns.md

# Building UI component?
cat docs/context/frontend/shadcn-components.md

# Working with vector search?
cat docs/context/database/postgresql-pgvector-patterns.md

# Setting up Docker?
cat docs/context/deployment/docker-compose-patterns.md
```

### Step 2: Copy Pattern to Your Code

```python
# Example: From fastapi-patterns.md
@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    db: AsyncSession = Depends(get_db),
    project_repo: ProjectRepository = Depends(get_project_repository)
):
    """List all projects (pattern from fastapi-patterns.md)."""
    projects = await project_repo.list_all()
    return projects
```

### Step 3: Reference Context Doc in Code

```python
# ✅ GOOD: Reference pattern source
async def similarity_search(query_embedding: List[float], top_k: int = 5):
    """
    Perform pgvector cosine similarity search.
    Pattern: docs/context/database/postgresql-pgvector-patterns.md
    """
    pass

# ❌ BAD: No reference to pattern source
async def search(query):
    pass
```

---

## 🔄 When to Update Context Docs

### Scenario 1: Library Upgrade

```bash
# FastAPI upgraded from 0.110 → 0.115
# Retrieve latest patterns via MCP
mcp__context7__get-library-docs("fastapi")
# → AI agent saves to docs/context/backend/fastapi-patterns.md

# Review changes, adapt to BMADFlow architecture
vim docs/context/backend/fastapi-patterns.md
```

### Scenario 2: Better Pattern Discovered

```bash
# During implementation, find improved official pattern
# Retrieve via MCP
mcp__shadcn__getComponent("data-table")
# → AI agent updates docs/context/frontend/shadcn-components.md

# Add changelog entry
## Updated 2025-10-06: Server-Side Pagination
- Added: DataTable with server-side pagination pattern
- Source: mcp__shadcn__getComponent("data-table")
```

### Scenario 3: New Library Added

```bash
# Adding new library to tech stack
# Retrieve patterns via MCP
mcp__context7__get-library-docs("pydantic")
# → Create docs/context/backend/pydantic-patterns.md

# Update Code Examples Policy to reference new doc
```

---

## 🤖 MCP Commands Reference

### Retrieve FastAPI Patterns
```bash
mcp__context7__get-library-docs("fastapi")
# → docs/context/backend/fastapi-patterns.md
```

### Retrieve shadcn/ui Components
```bash
mcp__shadcn__getComponent("table")
mcp__shadcn__getComponent("form")
mcp__shadcn__getComponent("dialog")
# → docs/context/frontend/shadcn-components.md
```

### Retrieve Database Patterns
```bash
mcp__context7__get-library-docs("pgvector")
mcp__context7__get-library-docs("sqlalchemy")
# → docs/context/database/postgresql-pgvector-patterns.md
```

### Retrieve Docker Patterns
```bash
mcp__context7__get-library-docs("docker-compose")
# → docs/context/deployment/docker-compose-patterns.md
```

---

## 📋 Context Docs Structure

```
docs/context/
├── README.md                           # Overview and quick navigation
├── HOW-TO-USE.md                       # This file
├── backend/
│   └── fastapi-patterns.md             # FastAPI: async routes, DI, Pydantic
├── frontend/
│   └── shadcn-components.md            # shadcn/ui: Table, Card, Form, Dialog
├── database/
│   └── postgresql-pgvector-patterns.md # PostgreSQL + pgvector: vector search
└── deployment/
    └── docker-compose-patterns.md      # Docker Compose: multi-service setup
```

---

## ⚠️ Important Rules

### DO ✅

- **Read context docs** before implementing features
- **Copy patterns** from context docs to your code
- **Reference context docs** in code comments
- **Use MCP services** to update context docs when libraries change
- **Update context docs** when discovering better official patterns

### DON'T ❌

- **Don't put BMADFlow code** in context docs (use `/backend/app/` or `/frontend/src/`)
- **Don't ignore context docs** and create custom patterns
- **Don't let context docs go stale** (update with library upgrades)
- **Don't skip MCP retrieval** when updating context docs (always get latest official patterns)

---

## 🔗 Related Documentation

- **Code Examples Policy**: [/docs/architecture/code-examples-policy.md](../architecture/code-examples-policy.md) - **MANDATORY READING**
- **Architecture Overview**: [/docs/architecture.md](../architecture.md)
- **Development Workflow**: [/docs/architecture/development-workflow.md](../architecture/development-workflow.md)
- **Tech Stack**: [/docs/architecture/tech-stack.md](../architecture/tech-stack.md)

---

## 💡 Tips

### Tip 1: Check Context Docs First
Before Googling or asking ChatGPT, check if the pattern is already in context docs.

### Tip 2: MCP Over Manual
Use MCP services to retrieve official patterns instead of manually copying from websites.

### Tip 3: Keep Changelogs
When updating context docs, always add a changelog entry with date and reason.

### Tip 4: Review Weekly
During sprint planning, quickly review context docs for staleness.

### Tip 5: Architecture References Context
If architecture doc example differs from context doc, context doc is authoritative.

---

**Remember**: Context docs are **living documentation** maintained throughout the development cycle. Keep them current, and they'll keep your implementation consistent! 📚✨

---
