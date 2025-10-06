# Development Workflow

## Daily Development Workflow

### Starting Development Session

**Hybrid Mode (Recommended for Development):**
```bash
# Terminal 1: Start database services
docker-compose -f docker-compose.hybrid.yml up -d

# Terminal 2: Start backend with hot reload
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Terminal 3: Start frontend with hot reload
cd frontend
npm run dev
```

**Full Docker Mode:**
```bash
docker-compose up
```

### Making Changes

**Backend Changes:**
1. Edit Python files in `backend/app/`
2. Save → uvicorn auto-reloads
3. Check logs for errors
4. Test endpoint via Swagger UI (http://localhost:8000/docs)

**Frontend Changes:**
1. Edit React files in `frontend/src/`
2. Save → Vite HMR updates browser
3. Check browser console for errors

**Database Schema Changes:**
1. Edit SQLAlchemy models in `backend/app/models/`
2. Generate migration: `alembic revision --autogenerate -m "Description"`
3. Review generated migration in `alembic/versions/`
4. Apply migration: `alembic upgrade head`
5. Restart backend

### Testing Changes

```bash
# Backend unit tests
cd backend
pytest tests/unit -v

# Backend integration tests (requires database)
pytest tests/integration -v

# Frontend component tests
cd frontend
npm test

# Frontend E2E tests
npm run test:e2e
```

### Code Quality Checks

**Backend:**
```bash
cd backend

# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking (optional)
mypy app/
```

**Frontend:**
```bash
cd frontend

# Format code
npm run format

# Lint code
npm run lint

# Type checking
npm run type-check
```

---

## Common Development Tasks

### Adding a New API Endpoint

1. **Define Pydantic schemas** (`backend/app/schemas/`)
2. **Create repository method** (`backend/app/repositories/`)
3. **Implement service logic** (`backend/app/services/`)
4. **Add API route** (`backend/app/api/v1/`)
5. **Write tests** (`backend/tests/`)
6. **Test via Swagger UI** (http://localhost:8000/docs)
7. **Update frontend API hook** (`frontend/src/api/hooks/`)

### Adding a New React Component

1. **Create component file** (`frontend/src/features/` or `frontend/src/components/`)
2. **Use shadcn/ui primitives** (e.g., `Button`, `Card`, `Dialog`)
3. **Add TypeScript types** (from `frontend/src/api/types/`)
4. **Integrate with API hooks** (`useProjects`, `useConversations`, etc.)
5. **Add to page** (`frontend/src/pages/`)
6. **Write component tests** (`frontend/tests/components/`)

### Adding a Database Table

1. **Create SQLAlchemy model** (`backend/app/models/`)
2. **Generate migration**: `alembic revision --autogenerate -m "Add table_name"`
3. **Review migration** (`alembic/versions/<timestamp>_add_table_name.py`)
4. **Apply migration**: `alembic upgrade head`
5. **Create Pydantic schemas** (`backend/app/schemas/`)
6. **Create repository** (`backend/app/repositories/`)
7. **Add API endpoints**
8. **Generate TypeScript types** (see section below)

### Generating TypeScript Types from Backend

**Script**: `backend/scripts/generate_types.py`

```python
# TODO: Implement type generation script
# Converts Pydantic schemas to TypeScript interfaces
# Output to frontend/src/api/types/
```

**Manual Type Sync (POC):**
```typescript
// frontend/src/api/types/project.ts
export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}
```

---

## Technical Documentation Reference

**During development, reference these implementation guides:**

### Backend Patterns
- **FastAPI Patterns**: `/docs/context/backend/fastapi-patterns.md`
- **PostgreSQL+pgvector**: `/docs/context/database/postgresql-pgvector-patterns.md`
- Use context7 MCP: `mcp__context7__get-library-docs` for FastAPI, SQLAlchemy, Pydantic

### Frontend Patterns
- **shadcn/ui Components**: `/docs/context/frontend/shadcn-components.md`
- Use shadcn MCP: `mcp__shadcn__getComponent` for component docs
- Use context7 MCP for React, TypeScript, Vite, TanStack Query docs

### Deployment Patterns
- **Docker Compose**: `/docs/context/deployment/docker-compose-patterns.md`

---

## Git Workflow

### Branch Strategy (POC Simplified)

**Single branch**: `main`

**Rationale**: 3-person team, POC scope, no production deployment

**Future**: Adopt Git Flow or GitHub Flow for production

### Commit Messages

**Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Build/tooling changes

**Examples**:
```
feat(backend): add vector similarity search endpoint

Implements POST /api/projects/{id}/search endpoint with
pgvector cosine similarity search.

Closes #42

---

fix(frontend): resolve CORS error in production build

Updated VITE_BACKEND_URL environment variable handling.

---

docs(architecture): add deployment section

Added Full Docker and Hybrid deployment instructions.
```

---

## Debugging

### Backend Debugging

**Print Debugging**:
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Project ID: {project_id}")
logger.info(f"Sync started for {project_doc.name}")
logger.error(f"GitHub API failed: {e}")
```

**Interactive Debugging (VS Code)**:
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

### Frontend Debugging

**Browser DevTools**:
- Console: Check for JavaScript errors, API responses
- Network: Inspect API calls, response status/payloads
- React DevTools: Inspect component state, props, hooks

**VS Code Debugging**:
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Chrome",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend/src"
    }
  ]
}
```

### Database Debugging

**pgAdmin**: http://localhost:5050
- Browse tables, run SQL queries, view data

**psql CLI**:
```bash
docker exec -it bmadflow-db psql -U bmadflow

# List tables
\dt

# Describe table
\d projects

# Query
SELECT * FROM projects;

# Exit
\q
```

---

## Documentation Requirements

### 🚨 MANDATORY: Keep Documentation in Sync

**Global Rule:** The [docs/](../docs/) folder MUST always be updated after any analysis or codebase modification.

When a story status changes, documentation MUST be updated. See [DOCUMENTATION-CONSISTENCY-RULES.md](../DOCUMENTATION-CONSISTENCY-RULES.md) for complete guidelines.

### Story Status Workflow

#### When Starting a Story
1. Create/update story file in `docs/stories/`
2. Set Status: "Ready" → "In Progress"
3. Begin implementation

#### During Implementation
1. **Update File List** as you create/modify files
2. **Add Implementation Notes** describing what you're building
3. **Update architecture docs** if patterns change
4. **Update context docs** if external patterns change (via MCP)

#### Before Moving to "Review"
**Pre-Review Checklist:**
- [ ] All acceptance criteria implemented
- [ ] **File List is complete** with all created/modified files
- [ ] **Implementation Notes** describe what was built
- [ ] All tests passing
- [ ] Architecture docs updated (if patterns changed)
- [ ] Context docs updated (if external patterns changed)

**Then:**
```bash
# Update story status
# Status: In Progress → Review

# Commit with story reference
git add .
git commit -m "feat(story-{epic}.{story}): {description}

- Implementation complete
- Updated story File List and Implementation Notes

Story: {epic}.{story}
Status: Review"
```

#### QA Review Process
1. QA runs: `/BMad/tasks/review-story`
2. QA adds **QA Results** section to story
3. QA creates quality gate file in `docs/qa/gates/`
4. QA recommends status change

#### After QA Review
1. Address any issues from QA Results
2. Update File List if new files added
3. If approved, update Status: "Review" → "Done"

### Pre-Commit Hook Automation

A git pre-commit hook automatically validates:
- Story files have required Status field
- Stories in "Review" have File List
- Stories in "Done" have QA Results
- Stories in "Done" have quality gate files

**Hook runs automatically on every commit.**

To bypass (not recommended): `git commit --no-verify`

### Documentation Update Guidelines

#### When Code Changes
Update in this order:
1. **Context Docs** ([docs/context/](../context/)) - If library patterns changed
2. **Architecture Docs** ([docs/architecture/](../)) - If system design changed
3. **Story Files** ([docs/stories/](../stories/)) - Always update File List
4. **PRD** ([docs/prd.md](../prd.md)) - Only if requirements changed

#### When Adding New Patterns

**Backend Pattern:**
```bash
# 1. Use MCP to get latest library docs
mcp__context7__get-library-docs("fastapi")

# 2. Update context doc
# Edit: docs/context/backend/fastapi-patterns.md

# 3. Add to story File List
# In story: docs/context/backend/fastapi-patterns.md - Updated with new pattern

# 4. Reference in code
# In code: """Pattern: docs/context/backend/fastapi-patterns.md"""
```

**Frontend Pattern:**
```bash
# 1. Use MCP to get component docs
mcp__shadcn__getComponent("dialog")

# 2. Update context doc
# Edit: docs/context/frontend/shadcn-components.md

# 3. Add to story File List
# In story: docs/context/frontend/shadcn-components.md - Updated with Dialog pattern

# 4. Reference in code
# In code: /* Pattern: docs/context/frontend/shadcn-components.md */
```

#### Architecture Changes
```bash
# 1. Identify which architecture doc needs update
# Example: database schema changed

# 2. Update the doc
# Edit: docs/architecture/database-schema.md

# 3. Add to story File List
# In story: docs/architecture/database-schema.md - Added new table definition

# 4. Note in Implementation Notes
# In story: "Updated database schema to support new feature X"
```

### Commit Message Format with Story Reference

**Required format when working on stories:**

```
<type>(story-{epic}.{story}): <subject>

<body>

Story: {epic}.{story}
Status: {current_status}
```

**Example:**
```
feat(story-1.3): implement user authentication

- Added JWT token generation
- Implemented login/logout endpoints
- Updated story 1.3 File List and Implementation Notes

Story: 1.3
Status: Review
```

### Weekly Documentation Audit

Run weekly to ensure consistency:

```bash
# Check for stories in "Done" without gate files
docs/scripts/check-story-gates.sh

# Check for stories in "Review" with empty File List
docs/scripts/check-file-lists.sh

# Generate documentation coverage report
docs/scripts/doc-coverage-report.sh
```

### Documentation Review Checklist

Before marking any story "Done", verify using [REVIEW-CHECKLIST.md](../REVIEW-CHECKLIST.md):

**Developer (Pre-Review):**
- [ ] Story file complete with all sections
- [ ] File List matches actual changes
- [ ] Implementation Notes describe what was built
- [ ] All tests passing

**QA (Review):**
- [ ] Run `/BMad/tasks/review-story`
- [ ] Verify File List accuracy
- [ ] Add QA Results section
- [ ] Create quality gate file
- [ ] Recommend status change

---

## Related Documentation

- **Documentation Consistency Rules**: [DOCUMENTATION-CONSISTENCY-RULES.md](../DOCUMENTATION-CONSISTENCY-RULES.md) - 🚨 **MANDATORY**
- **Review Checklist**: [REVIEW-CHECKLIST.md](../REVIEW-CHECKLIST.md)
- **Documentation Map**: [DOCUMENTATION-MAP.md](../DOCUMENTATION-MAP.md)
- **Source Tree**: [source-tree.md](source-tree.md)
- **Deployment**: [deployment.md](deployment.md)
- **Testing Strategy**: [testing-strategy.md](testing-strategy.md)
- **Coding Standards**: [coding-standards.md](coding-standards.md)

---
