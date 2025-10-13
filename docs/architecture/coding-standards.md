# Coding Standards

## Overview

BMADFlow follows industry-standard coding conventions for Python (PEP 8 via Black/Ruff) and TypeScript (ESLint + Prettier). This document defines critical rules, patterns, and best practices for consistent, maintainable code.

---

## Python (Backend)

### Code Formatting

**Tools**: Black (formatter) + Ruff (linter)

**Configuration**:
```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Line length handled by Black
```

**Format Code**:
```bash
black app/ tests/
ruff check app/ tests/ --fix
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | `snake_case` | `project_service.py` |
| Classes | `PascalCase` | `ProjectService` |
| Functions | `snake_case` | `get_project_by_id()` |
| Variables | `snake_case` | `project_id` |
| Constants | `UPPER_SNAKE_CASE` | `EMBEDDING_DIM` |
| Private | `_leading_underscore` | `_internal_method()` |

### Type Hints

**Required for all functions:**
```python
from typing import Optional, List
from uuid import UUID

async def get_project_by_id(project_id: UUID) -> Optional[Project]:
    """Retrieve project by ID."""
    return await project_repo.get_by_id(project_id)
```

### Docstrings

**Google Style**:
```python
def process_document(content: str, file_type: str) -> List[Chunk]:
    """Process document content into chunks.

    Args:
        content: Raw document content
        file_type: File extension (md, csv, yaml, json)

    Returns:
        List of processed chunks with metadata

    Raises:
        ValueError: If file_type is unsupported
    """
    pass
```

### Async/Await

**Use async for I/O operations:**
```python
# Good: Async for database/API calls
async def fetch_from_github(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Bad: Blocking call
def fetch_from_github(url: str) -> dict:
    response = requests.get(url)  # Blocks event loop
    return response.json()
```

### Error Handling

**Use specific exceptions:**
```python
from fastapi import HTTPException

async def get_project(project_id: UUID) -> Project:
    project = await project_repo.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    return project
```

### Critical Rules

1. **No hardcoded credentials**: Use environment variables
2. **No SQL injection**: Use SQLAlchemy ORM, parameterized queries
3. **Validate input**: Use Pydantic schemas for all API inputs
4. **Log errors**: Use structured logging, not print()
5. **Handle async properly**: Avoid blocking calls in async functions

---

## TypeScript/React (Frontend)

### Code Formatting

**Tools**: ESLint + Prettier

**Configuration**:
```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-script/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "no-console": "warn",
    "@typescript-eslint/no-unused-vars": "error"
  }
}

// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100
}
```

**Format Code**:
```bash
npm run format
npm run lint -- --fix
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | `PascalCase.tsx` | `ProjectCard.tsx` |
| Hooks | `camelCase.ts` (use prefix) | `useProjects.ts` |
| Functions | `camelCase` | `fetchProjects()` |
| Variables | `camelCase` | `projectId` |
| Constants | `UPPER_SNAKE_CASE` | `API_BASE_URL` |
| Types/Interfaces | `PascalCase` | `Project`, `ProjectCardProps` |

### Component Structure

**Functional components with TypeScript:**
```tsx
interface ProjectCardProps {
  project: Project;
  onSelect?: (id: string) => void;
}

export function ProjectCard({ project, onSelect }: ProjectCardProps) {
  const handleClick = () => {
    onSelect?.(project.id);
  };

  return (
    <Card onClick={handleClick}>
      <CardHeader>
        <CardTitle>{project.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>{project.description}</p>
      </CardContent>
    </Card>
  );
}
```

### Hooks Rules

**Follow Rules of Hooks:**
1. Only call hooks at top level (not inside loops/conditions)
2. Only call hooks from React functions
3. Custom hooks must start with `use`

```tsx
// Good
function MyComponent() {
  const [state, setState] = useState(0);

  useEffect(() => {
    // Side effect
  }, []);

  return <div>{state}</div>;
}

// Bad: Hook inside condition
function MyComponent({ condition }) {
  if (condition) {
    const [state, setState] = useState(0);  // ❌ Error
  }
  return <div />;
}
```

### State Management

**Prefer local state, use Zustand for global:**
```tsx
// Local state for component-specific UI
function FileTreePanel() {
  const [selectedNode, setSelectedNode] = useState<FileNode | null>(null);
  // ...
}

// Global state for app-wide concerns
import { useAppStore } from '@/store/appStore';

function Sidebar() {
  const { selectedProjectId, setSelectedProjectId } = useAppStore();
  // ...
}
```

### API Calls

**Use React Query hooks:**
```tsx
// Good: React Query handles caching, loading, errors
function ProjectList() {
  const { data: projects, isLoading, error } = useProjects();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;

  return <div>{projects.map(p => <ProjectCard key={p.id} project={p} />)}</div>;
}

// Bad: Manual state management
function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/projects')
      .then(res => res.json())
      .then(setProjects)
      .finally(() => setLoading(false));
  }, []);
  // ...
}
```

### Accessibility

**WCAG 2.1 AA compliance:**
```tsx
// Good: Semantic HTML + ARIA
<button
  onClick={handleClick}
  aria-label="Delete project"
  className="..."
>
  <TrashIcon />
</button>

// Bad: div as button
<div onClick={handleClick}>  // ❌ Not keyboard accessible
  <TrashIcon />
</div>
```

### Critical Rules

1. **Always define prop types**: Use TypeScript interfaces
2. **Key prop for lists**: Unique, stable keys (not array index)
3. **Avoid inline functions**: Extract handlers for performance
4. **Memoize expensive computations**: Use `useMemo`, `useCallback`
5. **Clean up effects**: Return cleanup function from `useEffect`

---

## SQL (Database)

### Schema Naming

| Type | Convention | Example |
|------|------------|---------|
| Tables | `snake_case` (plural) | `projects`, `project_docs` |
| Columns | `snake_case` | `project_id`, `created_at` |
| Indexes | `{table}_{column}_idx` | `projects_name_idx` |
| Foreign Keys | `{table}_{ref_table}_fkey` | `project_docs_project_id_fkey` |

### Query Optimization

**Use indexes for foreign keys and filters:**
```sql
-- Good: Index on frequently queried column
CREATE INDEX chunks_document_id_idx ON chunks(document_id);

-- Good: Composite index for multi-column queries
CREATE INDEX conversations_project_updated_idx
ON conversations(project_id, updated_at DESC);
```

**Avoid N+1 queries:**
```python
# Good: Eager loading with joinedload
projects = await session.execute(
    select(Project).options(joinedload(Project.project_docs))
)

# Bad: N+1 problem (queries for each project)
projects = await session.execute(select(Project))
for project in projects:
    docs = await session.execute(
        select(ProjectDoc).where(ProjectDoc.project_id == project.id)
    )  # ❌ Separate query per project
```

---

## Git

### Commit Messages

**Format**: `<type>(<scope>): <subject>`

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Examples**:
```
feat(backend): add vector similarity search endpoint
fix(frontend): resolve file tree scroll issue
docs(architecture): update deployment section
refactor(backend): extract GitHub service from sync logic
test(frontend): add ProjectCard component tests
chore(deps): upgrade FastAPI to 0.110.0
```

---

## Backend-Frontend Type Alignment

**Pattern Discovered**: Epic 5 Story 5.5 (backend missing `file_name` field caused frontend type mismatch)

### 🎯 Critical Pattern: Explicit Field Serialization

**Why This Matters:**
- **Problem**: Backend Pydantic schemas missing fields → frontend derives from other fields (fragile, error-prone)
- **Solution**: Backend must explicitly serialize ALL fields frontend expects in Pydantic response schemas
- **Impact**: Prevents integration test failures, reduces defensive coding, improves type safety

**Example Issue from Epic 5:**

```python
# ❌ BAD: Backend missing file_name field
class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None  # ← Missing explicit typing
    created_at: datetime

# Backend serialization (incomplete)
sources_json = [
    {
        "document_id": str(chunk.document_id),
        "file_path": chunk.file_path,
        "header_anchor": chunk.header_anchor,
        "similarity_score": chunk.similarity_score,
        # ❌ Missing file_name → frontend derives from file_path
    }
    for chunk in chunks
]
```

```typescript
// ❌ FRAGILE: Frontend derives file_name from file_path
interface SourceDocument {
  document_id: string;
  file_path: string;
  file_name: string;  // Expected but not provided by backend
  header_anchor: string | null;
  similarity_score: number;
}

// Defensive fallback logic (fragile)
const fileName = source.file_name || source.file_path.split('/').pop() || 'unknown';
```

**Correct Implementation:**

```python
# ✅ CORRECT: Backend explicitly serializes all fields
class SourceDocument(BaseModel):
    """Source document reference in assistant message."""
    document_id: UUID
    file_path: str
    file_name: str  # ← Explicitly included
    header_anchor: Optional[str] = None
    similarity_score: float

class MessageResponse(BaseModel):
    """Message response with typed sources."""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    sources: Optional[List[SourceDocument]] = None  # ← Typed with schema
    created_at: datetime

# Backend serialization (complete)
sources_json = [
    {
        "document_id": str(chunk.document_id),
        "file_path": chunk.file_path,
        "file_name": chunk.file_path.split('/')[-1],  # ← Explicitly calculated
        "header_anchor": chunk.header_anchor,
        "similarity_score": chunk.similarity_score,
    }
    for chunk in chunks
]
```

```typescript
// ✅ CORRECT: Frontend types match backend schema exactly
interface SourceDocument {
  document_id: string;
  file_path: string;
  file_name: string;  // ← Backend provides this explicitly
  header_anchor: string | null;
  similarity_score: number;
}

// No defensive fallback needed - backend guarantees field presence
const fileName = source.file_name;  // Always present
```

### Best Practices for Type Alignment

#### 1. Backend Pydantic Schemas

**Always create explicit schemas for nested objects:**

```python
# Good: Explicit nested schema
class SourceDocument(BaseModel):
    document_id: UUID
    file_path: str
    file_name: str  # Don't assume frontend can derive this
    header_anchor: Optional[str] = None
    similarity_score: float

class MessageResponse(BaseModel):
    sources: Optional[List[SourceDocument]] = None

# Bad: Generic dict (no type contract)
class MessageResponse(BaseModel):
    sources: Optional[List[Dict[str, Any]]] = None  # ❌ No type safety
```

#### 2. Frontend TypeScript Types

**Mirror backend Pydantic schemas exactly:**

```typescript
// Good: Exact mirror of backend SourceDocument schema
interface SourceDocument {
  document_id: string;  // UUID → string
  file_path: string;
  file_name: string;
  header_anchor: string | null;  // Optional[str] → string | null
  similarity_score: number;  // float → number
}

// Bad: Frontend adds extra fields backend doesn't provide
interface SourceDocument {
  document_id: string;
  file_path: string;
  file_name: string;
  header_anchor: string | null;
  similarity_score: number;
  display_name?: string;  // ❌ Not in backend schema → will be undefined
}
```

#### 3. Timezone Handling

**Pattern from Epic 5 Story 5.3:**

```python
# ✅ CORRECT: Use func.now() for server-side timestamps
from sqlalchemy import func

class Conversation(Base):
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

# ❌ INCORRECT: Use datetime.utcnow() (no timezone info)
from datetime import datetime

class Conversation(Base):
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # No TZ
```

### Automated Validation (Recommended)

**1. Contract Testing (Pact or similar):**

```typescript
// frontend/tests/api-contracts/message-sources-contract.test.ts
import { MessageResponse } from '@/api/types/message';
import { openApiSchema } from '@/generated/openapi-schema';

test('MessageResponse sources field matches OpenAPI schema', () => {
  const sourceSchema = openApiSchema.components.schemas.MessageResponse.properties.sources.items;

  // Validate required fields present
  expect(sourceSchema.required).toContain('document_id');
  expect(sourceSchema.required).toContain('file_path');
  expect(sourceSchema.required).toContain('file_name');  // ← Would catch missing field
  expect(sourceSchema.required).toContain('header_anchor');
  expect(sourceSchema.required).toContain('similarity_score');
});
```

**2. Auto-Generated Types (pydantic-to-typescript):**

```bash
# Generate TypeScript types from Pydantic schemas
pydantic-to-typescript backend/app/schemas/message.py --output frontend/src/api/types/message.generated.ts
```

### Code Review Checklist

#### Backend Type Contract
- [ ] All Pydantic response schemas explicitly define nested objects (no `Dict[str, Any]`)
- [ ] Backend serializes ALL fields frontend types expect (no assumed derivations)
- [ ] OpenAPI schema generated and committed (`fastapi` generates this automatically)
- [ ] Timestamps use `func.now()` for timezone consistency

#### Frontend Type Contract
- [ ] TypeScript types mirror backend Pydantic schemas exactly
- [ ] No extra fields in frontend types that backend doesn't provide
- [ ] UUID fields typed as `string` (not `UUID` - that's a Python type)
- [ ] Optional fields use `| null` (not `| undefined` - backend sends `null`)

#### Type Alignment Validation
- [ ] Integration tests mock data includes ALL fields (e.g., `file_name` in sources)
- [ ] Contract tests validate frontend types match OpenAPI schema (optional but recommended)
- [ ] No defensive fallback logic for "missing" fields (if needed, backend schema is incomplete)

---

## Code Review Checklist

### Backend
- [ ] Type hints on all functions
- [ ] Pydantic schemas for request/response
- [ ] **Explicit schemas for nested objects (no `Dict[str, Any]`)**
- [ ] **All fields frontend expects explicitly serialized**
- [ ] Error handling with appropriate HTTP status codes
- [ ] Unit tests for business logic (70%+ coverage)
- [ ] No hardcoded credentials
- [ ] Async/await used correctly
- [ ] Logging for important operations
- [ ] **Timestamps use `func.now()` for timezone consistency**

### Frontend
- [ ] TypeScript types for props and state
- [ ] **Frontend types mirror backend Pydantic schemas exactly**
- [ ] Accessibility attributes (aria-label, semantic HTML)
- [ ] Loading and error states handled
- [ ] Component tests with React Testing Library
- [ ] No console.log in production code
- [ ] Memoization for expensive operations
- [ ] React Query for API calls

### Database
- [ ] Alembic migration created
- [ ] Foreign keys with ON DELETE CASCADE
- [ ] Indexes on frequently queried columns
- [ ] No raw SQL (use SQLAlchemy ORM)

---

## Related Documentation

- **Backend Architecture**: [backend-architecture.md](backend-architecture.md)
- **Frontend Architecture**: [frontend-architecture.md](frontend-architecture.md)
- **Testing Strategy**: [testing-strategy.md](testing-strategy.md)
- **Development Workflow**: [development-workflow.md](development-workflow.md)

---
