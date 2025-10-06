# Testing Strategy

## Overview

BMADFlow follows a **testing pyramid** approach with comprehensive backend coverage (70%+ target per NFR18), component-level frontend testing, and E2E validation of critical user flows using Playwright. Testing ensures reliability while maintaining development velocity appropriate for a POC.

> **📚 Comprehensive QA Documentation Available:**
> This testing strategy provides technical implementation details. For comprehensive test-first development guides, quality gates, and Playwright MCP integration, see:
> - **[QA Documentation Hub](../qa/README.md)** - Central QA documentation index with quick start guides
> - **[Early Test Architecture](../qa/early-test-architecture.md)** - Test-first patterns from Story 1.1, RED-GREEN-REFACTOR, test data management
> - **[Playwright MCP E2E Strategy](../qa/playwright-mcp-e2e-strategy.md)** - E2E scenarios, visual regression, debug workflows, 6-gate quality checklist

## Testing Pyramid

```mermaid
graph TB
    E2E[E2E Tests<br/>Playwright<br/>Critical Flows]
    INT[Integration Tests<br/>API + Database + External Services]
    UNIT[Unit Tests<br/>Services, Repositories, Components<br/>70%+ Backend Coverage]

    E2E --> INT --> UNIT

    style E2E fill:#cf222e
    style INT fill:#bf8700
    style UNIT fill:#1a7f37
```

---

## Backend Testing

### Unit Tests (pytest)

**Purpose**: Test business logic in isolation with mocked dependencies

**Location**: `backend/tests/unit/`

**Coverage Target**: 70%+ for services, repositories, utils

**Example: Service Unit Test**
```python
# tests/unit/services/test_project_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.project_service import ProjectService
from app.schemas.project import CreateProjectRequest

@pytest.mark.asyncio
async def test_create_project_success():
    # Arrange
    mock_repo = Mock()
    mock_repo.create = AsyncMock(return_value={"id": "123", "name": "Test Project"})
    service = ProjectService(project_repo=mock_repo)

    request = CreateProjectRequest(name="Test Project", description="Test")

    # Act
    result = await service.create_project(request)

    # Assert
    assert result["name"] == "Test Project"
    mock_repo.create.assert_called_once()
```

**Example: Repository Unit Test (with Test Database)**
```python
# tests/unit/repositories/test_project_repository.py
import pytest
from app.repositories.project_repository import ProjectRepository
from app.models.project import Project

@pytest.mark.asyncio
async def test_get_project_by_id(db_session):
    # Arrange
    repo = ProjectRepository(db_session)
    project = Project(name="Test", description="Test project")
    db_session.add(project)
    await db_session.commit()

    # Act
    result = await repo.get_by_id(project.id)

    # Assert
    assert result.name == "Test"
```

**Run Unit Tests:**
```bash
cd backend
pytest tests/unit -v --cov=app --cov-report=html
```

### Integration Tests

**Purpose**: Test API endpoints, database operations, external integrations

**Location**: `backend/tests/integration/`

**Example: API Integration Test**
```python
# tests/integration/api/test_projects_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_project_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/projects",
            json={"name": "Test Project", "description": "Test"}
        )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data
```

**Example: GitHub Integration Test (with Mocking)**
```python
# tests/integration/external/test_github_service.py
import pytest
from unittest.mock import patch
from app.services.github_service import GitHubService

@pytest.mark.asyncio
@patch("app.services.github_service.httpx.AsyncClient.get")
async def test_fetch_repository_files(mock_get):
    # Arrange
    mock_response = Mock()
    mock_response.json.return_value = {
        "tree": [
            {"path": "README.md", "type": "blob"},
            {"path": "docs/prd.md", "type": "blob"}
        ]
    }
    mock_get.return_value = mock_response

    service = GitHubService()

    # Act
    files = await service.fetch_repository_files("owner/repo")

    # Assert
    assert len(files) == 2
    assert files[0]["path"] == "README.md"
```

**Run Integration Tests:**
```bash
pytest tests/integration -v
```

### Test Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.database import Base

@pytest.fixture
async def db_session():
    """Provide a test database session."""
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for embedding tests."""
    with patch("app.services.embedding_service.ollama") as mock:
        mock.embeddings.return_value = {"embedding": [0.1] * 768}
        yield mock
```

---

## Frontend Testing

### Component Tests (React Testing Library)

**Purpose**: Test React components in isolation with user-centric assertions

**Location**: `frontend/tests/components/`

**Example: Component Test**
```tsx
// tests/components/ProjectCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProjectCard } from '@/features/projects/ProjectCard';

describe('ProjectCard', () => {
  const mockProject = {
    id: '123',
    name: 'Test Project',
    description: 'Test description',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  };

  it('renders project name and description', () => {
    render(<ProjectCard project={mockProject} />);

    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('calls onSelect when clicked', () => {
    const mockOnSelect = jest.fn();
    render(<ProjectCard project={mockProject} onSelect={mockOnSelect} />);

    fireEvent.click(screen.getByText('View Project'));

    expect(mockOnSelect).toHaveBeenCalledWith('123');
  });
});
```

**Run Component Tests:**
```bash
cd frontend
npm test
```

### Hook Tests

**Example: API Hook Test**
```tsx
// tests/hooks/useProjects.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useProjects } from '@/api/hooks/useProjects';
import { apiClient } from '@/api/client';

jest.mock('@/api/client');

describe('useProjects', () => {
  const queryClient = new QueryClient();
  const wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('fetches projects successfully', async () => {
    (apiClient.get as jest.Mock).mockResolvedValue({
      data: [{ id: '1', name: 'Project 1' }],
    });

    const { result } = renderHook(() => useProjects(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual([{ id: '1', name: 'Project 1' }]);
  });
});
```

---

## End-to-End Tests (Playwright)

### Test Scenarios

**Critical User Flows (per NFR21):**
1. **Browse Documentation**: Navigate file tree, view markdown/CSV files
2. **Sync ProjectDoc**: Trigger sync, verify completion
3. **AI Chat**: Send message, receive response with sources

**Location**: `frontend/tests/e2e/`

**Example: E2E Test**
```typescript
// tests/e2e/browse-documentation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Browse Documentation', () => {
  test('should navigate file tree and view markdown file', async ({ page }) => {
    // Navigate to Explorer
    await page.goto('http://localhost:3000/projects/123/explorer');

    // Wait for file tree to load
    await page.waitForSelector('[data-testid="file-tree"]');

    // Expand folder
    await page.click('text=docs');

    // Click file
    await page.click('text=README.md');

    // Verify content viewer displays markdown
    await expect(page.locator('[data-testid="content-viewer"]')).toContainText('# BMADFlow');

    // Verify TOC is generated
    await expect(page.locator('[data-testid="table-of-contents"]')).toBeVisible();
  });
});
```

**Example: Sync Test**
```typescript
// tests/e2e/sync-project-doc.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Sync ProjectDoc', () => {
  test('should trigger sync and show completion', async ({ page }) => {
    await page.goto('http://localhost:3000/projects/123');

    // Click sync button
    await page.click('[data-testid="sync-button"]');

    // Verify loading state
    await expect(page.locator('text=Syncing...')).toBeVisible();

    // Wait for success toast (max 60s for sync operation)
    await expect(page.locator('text=Sync completed successfully')).toBeVisible({ timeout: 60000 });

    // Verify sync timestamp updated
    const timestamp = await page.locator('[data-testid="last-synced"]').textContent();
    expect(timestamp).toContain('seconds ago');
  });
});
```

**Run E2E Tests:**
```bash
cd frontend
npm run test:e2e

# Run specific test file
npx playwright test tests/e2e/browse-documentation.spec.ts

# Run in UI mode (interactive)
npx playwright test --ui
```

### Playwright MCP Integration

**Purpose**: AI-assisted E2E testing via Playwright MCP (per FR37-39, FR44)

**Use Cases:**
1. **Programmatic Frontend Launch**: `mcp__playwright__browser_navigate`
2. **Screenshot Capture**: `mcp__playwright__browser_take_screenshot`
3. **Console Log Monitoring**: `mcp__playwright__browser_console_messages`
4. **Manual Test Plan Generation**: Ask agent to generate test plans

**Example: Using Playwright MCP**
```
User: "Take a screenshot of the Dashboard page"

Agent uses:
1. mcp__playwright__browser_navigate("http://localhost:3000")
2. mcp__playwright__browser_snapshot() or mcp__playwright__browser_take_screenshot()
3. Returns screenshot for user review
```

---

## Test Coverage

### Measuring Coverage

**Backend:**
```bash
cd backend
pytest --cov=app --cov-report=html --cov-report=term
open htmlcov/index.html  # View HTML report
```

**Frontend:**
```bash
cd frontend
npm test -- --coverage
open coverage/lcov-report/index.html
```

### Coverage Targets

| Layer | Target | Actual (TBD) |
|-------|--------|--------------|
| Backend Services | 70%+ | - |
| Backend Repositories | 70%+ | - |
| Frontend Components | 60%+ | - |
| E2E Critical Flows | 100% | - |

---

## Mocking Strategies

### Mocking External APIs

**GitHub API:**
```python
@patch("app.services.github_service.httpx.AsyncClient.get")
async def test_github_fetch(mock_get):
    mock_get.return_value.json.return_value = {"files": [...]}
    # Test logic
```

**Ollama API:**
```python
@pytest.fixture
def mock_ollama():
    with patch("ollama.embeddings") as mock:
        mock.return_value = {"embedding": [0.1] * 768}
        yield mock
```

**LLM Providers:**
```python
@patch("app.services.llm_service.openai.ChatCompletion.create")
async def test_chatbot_response(mock_llm):
    mock_llm.return_value = {"choices": [{"message": {"content": "Response"}}]}
    # Test RAG agent
```

### Mocking Database (Test Database)

**Use in-memory SQLite for fast unit tests:**
```python
@pytest.fixture
async def memory_db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # Create tables, return session
```

**Use PostgreSQL test database for integration tests:**
```bash
# Create test database
createdb test_bmadflow

# Run migrations
DATABASE_URL=postgresql://localhost/test_bmadflow alembic upgrade head
```

---

## Continuous Testing (Future)

**POC**: Manual test execution

**Production**: CI/CD pipeline with automated testing
```yaml
# .github/workflows/test.yml (Future)
name: Test

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run frontend tests
        run: |
          cd frontend
          npm ci
          npm test -- --coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E tests
        run: |
          docker-compose up -d
          cd frontend
          npx playwright test
```

---

## Test Data Management

### Seed Scripts

**Purpose**: Populate test data for manual testing

**Script**: `backend/scripts/seed_data.py`

```python
# Example seed script
async def seed_test_data():
    # Create test project
    project = await project_repo.create(name="Test Project", description="Sample project")

    # Create test ProjectDoc
    project_doc = await project_doc_repo.create(
        project_id=project.id,
        name="AgentLab Docs",
        github_url="https://github.com/example/agentlab",
        github_folder_path="docs"
    )

    # Create test LLM provider
    await llm_provider_repo.create(
        provider_name="ollama",
        model_name="llama2",
        is_default=True
    )

    print("Test data seeded successfully")
```

**Run Seed Script:**
```bash
cd backend
python scripts/seed_data.py
```

---

## Related Documentation

### Architecture Documentation
- **Development Workflow**: [development-workflow.md](development-workflow.md)
- **Coding Standards**: [coding-standards.md](coding-standards.md)
- **High-Level Architecture**: [high-level-architecture.md](high-level-architecture.md)

### QA Documentation (Comprehensive Testing Guides)
- **QA Documentation Hub**: [../qa/README.md](../qa/README.md) - Central QA documentation index
- **Early Test Architecture**: [../qa/early-test-architecture.md](../qa/early-test-architecture.md) - Test-first development guide from Story 1.1
- **Playwright MCP E2E Strategy**: [../qa/playwright-mcp-e2e-strategy.md](../qa/playwright-mcp-e2e-strategy.md) - Comprehensive E2E testing with Playwright MCP

### Requirements Documentation
- **PRD Testing Requirements**: [../prd.md#testing-requirements](../prd.md)

---
