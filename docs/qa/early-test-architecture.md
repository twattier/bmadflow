# Early Test Architecture

**Document Type:** QA Architecture Guide
**Owner:** Quinn (Test Architect)
**Status:** Approved
**Last Updated:** 2025-10-06

## Executive Summary

This document defines the **test-first architecture** for BMADFlow, establishing comprehensive testing practices from Story 1.1. Tests are not an afterthought—they are **architectural components** that shape system design, ensure quality gates, and enable confident refactoring.

**Core Philosophy:** Build test infrastructure BEFORE application code, write tests FIRST, then implement to pass.

---

## Test Architecture Framework

### Layer 1: Test Infrastructure (Story 1.1-1.3)

#### Philosophy: Test Setup Before Code

**Critical Principle:** Epic 1 foundation stories must establish complete test infrastructure before any application logic.

#### Directory Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures (DB sessions, mocks)
│   ├── unit/                    # Service/Repository unit tests
│   │   ├── services/
│   │   ├── repositories/
│   │   └── utils/
│   ├── integration/             # API/DB integration tests
│   │   ├── api/
│   │   ├── external/            # GitHub, Ollama mocks
│   │   └── database/
│   └── fixtures/                # Test data builders
│       ├── builders.py
│       └── factories.py
├── requirements.txt             # Production dependencies
└── requirements-test.txt        # Test-only dependencies

frontend/
├── tests/
│   ├── setup.ts                 # Global test configuration
│   ├── components/              # React component tests
│   ├── hooks/                   # Custom hook tests
│   ├── e2e/                     # Playwright E2E tests
│   │   ├── critical-flows/
│   │   ├── visual-regression/
│   │   └── setup/
│   └── fixtures/                # Mock data factories
│       └── factories.ts
├── vitest.config.ts             # Vitest configuration
└── playwright.config.ts         # Playwright configuration
```

---

### Layer 2: Test-First Development Patterns

#### Pattern 1: RED-GREEN-REFACTOR (All Stories)

**Story Example: 2.1 - Create Project Database Schema and API**

**Step 1 - RED (Write Failing Test):**

```python
# tests/integration/api/test_projects_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_project_endpoint():
    """Test POST /api/projects creates a project."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/projects",
            json={"name": "Test Project", "description": "Test Description"}
        )

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"
    assert "id" in data
    assert "created_at" in data

# RUN: pytest tests/integration/api/test_projects_api.py
# EXPECTED: FAIL - Endpoint doesn't exist yet
```

**Step 2 - GREEN (Minimal Implementation):**

```python
# app/api/routes/projects.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.project import Project
from app.schemas.project import CreateProjectRequest, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
async def create_project(
    request: CreateProjectRequest,
    session: AsyncSession = Depends(get_session)
):
    """Create a new project."""
    # Minimal code to pass test
    project = Project(name=request.name, description=request.description)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project

# RUN: pytest tests/integration/api/test_projects_api.py
# EXPECTED: PASS - Test now passes with minimal implementation
```

**Step 3 - REFACTOR (Extract to Service Layer):**

```python
# app/services/project_service.py
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import CreateProjectRequest

class ProjectService:
    """Business logic for Project operations."""

    def __init__(self, project_repo: ProjectRepository):
        self.project_repo = project_repo

    async def create_project(self, request: CreateProjectRequest):
        """Create project with business logic."""
        # Add validation, business rules, etc.
        return await self.project_repo.create(request)

# app/api/routes/projects.py (updated)
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    service: ProjectService = Depends(get_project_service)
):
    """Create a new project (refactored to use service)."""
    return await service.create_project(request)

# RUN: pytest tests/integration/api/test_projects_api.py
# EXPECTED: PASS - Test still passes after refactor (design validated)
```

---

#### Pattern 2: Mock External Dependencies (Epic 2-4)

**Story Example: 2.3 - GitHub API Integration**

**Test Strategy: Mock GitHub, Test Business Logic**

```python
# tests/integration/external/test_github_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.github_service import GitHubService

@pytest.mark.asyncio
@patch("app.services.github_service.httpx.AsyncClient.get")
async def test_fetch_repository_files(mock_get):
    """Test GitHub file fetching with mocked API."""

    # Arrange - Mock GitHub API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "tree": [
            {"path": "README.md", "type": "blob", "url": "https://..."},
            {"path": "docs/prd.md", "type": "blob", "url": "https://..."},
            {"path": "src/", "type": "tree", "url": "https://..."}  # Folder, should be filtered
        ]
    }
    mock_response.headers = {
        "X-RateLimit-Remaining": "59",
        "X-RateLimit-Reset": "1609459200"
    }
    mock_get.return_value = mock_response

    service = GitHubService()

    # Act
    files = await service.fetch_repository_files(
        owner="test-owner",
        repo="test-repo",
        folder_path="docs"
    )

    # Assert - Business logic tested, not GitHub infrastructure
    assert len(files) == 2  # Tree filtered out
    assert files[0]["path"] == "README.md"
    assert files[1]["path"] == "docs/prd.md"
    assert mock_get.call_count == 1

    # Verify rate limit tracking
    call_args = mock_get.call_args
    assert "tree" in call_args[0][0]  # GitHub tree API called
```

**Story Example: 4.2 - Ollama Embedding Generation**

**Test Strategy: Mock Ollama, Validate Dimensions**

```python
# tests/unit/services/test_embedding_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.embedding_service import EmbeddingService

@pytest.mark.asyncio
async def test_generate_embedding(mock_ollama_client):
    """Test embedding generation with mocked Ollama."""

    # Arrange - Mock 768-dimensional vector
    mock_ollama_client.embeddings = AsyncMock(return_value={
        "embedding": [0.1] * 768
    })

    service = EmbeddingService(ollama_client=mock_ollama_client)

    # Act
    embedding = await service.generate_embedding("test text for embedding")

    # Assert - Validate dimension and data type
    assert len(embedding) == 768  # nomic-embed-text dimension (NFR requirement)
    assert all(isinstance(x, float) for x in embedding)

    # Verify Ollama called correctly
    mock_ollama_client.embeddings.assert_called_once_with(
        model="nomic-embed-text",
        prompt="test text for embedding"
    )

# conftest.py fixture for mock Ollama
@pytest.fixture
def mock_ollama_client():
    """Provide mocked Ollama client."""
    with patch("app.services.embedding_service.ollama") as mock:
        yield mock
```

---

#### Pattern 3: Test Data Builders (All Epics)

**Fixture Pattern: Reusable, Readable Test Data**

```python
# tests/fixtures/builders.py
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.project_doc import ProjectDoc

@dataclass
class ProjectBuilder:
    """Builder for Project test data."""
    name: str = "Test Project"
    description: str = "Test Description"

    def with_name(self, name: str):
        """Set project name."""
        self.name = name
        return self

    def with_description(self, description: str):
        """Set project description."""
        self.description = description
        return self

    async def build(self, session: AsyncSession) -> Project:
        """Build and persist project."""
        project = Project(name=self.name, description=self.description)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

@dataclass
class ProjectDocBuilder:
    """Builder for ProjectDoc test data."""
    project_id: Optional[str] = None
    name: str = "Test ProjectDoc"
    github_url: str = "https://github.com/test/repo"
    github_folder_path: str = "docs"

    def for_project(self, project_id: str):
        """Associate with project."""
        self.project_id = project_id
        return self

    def with_github_url(self, url: str):
        """Set GitHub URL."""
        self.github_url = url
        return self

    async def build(self, session: AsyncSession) -> ProjectDoc:
        """Build and persist ProjectDoc."""
        doc = ProjectDoc(
            project_id=self.project_id,
            name=self.name,
            github_url=self.github_url,
            github_folder_path=self.github_folder_path
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        return doc

# Usage in tests - Clean, readable test data creation
@pytest.mark.asyncio
async def test_project_with_multiple_docs(db_session):
    """Test project can have multiple ProjectDocs."""

    # Arrange - Fluent builder pattern
    project = await ProjectBuilder() \
        .with_name("BMAD Documentation Hub") \
        .with_description("Central docs for BMAD projects") \
        .build(db_session)

    doc1 = await ProjectDocBuilder() \
        .for_project(project.id) \
        .with_github_url("https://github.com/bmad/agentlab") \
        .build(db_session)

    doc2 = await ProjectDocBuilder() \
        .for_project(project.id) \
        .with_github_url("https://github.com/bmad/magnet") \
        .build(db_session)

    # Assert
    assert doc1.project_id == project.id
    assert doc2.project_id == project.id
```

---

### Layer 3: Test Data Management Strategy

#### Strategy 1: Test Database Lifecycle

**Isolation Levels:**

1. **Session-scoped** (shared across all tests in session)
   - Engine creation
   - Schema migrations
   - One-time setup

2. **Function-scoped** (isolated per test)
   - Database transactions
   - Test data insertion
   - Automatic rollback

**Implementation:**

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.database import Base
from app.config import get_settings

settings = get_settings()
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/bmadflow_test"

# Session-scoped: Create test database engine once
@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine (session-scoped)."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,  # Log SQL queries for debugging
        future=True
    )

    # Create schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup: Drop schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

# Function-scoped: Isolated transaction per test
@pytest.fixture
async def db_session(test_engine):
    """Provide isolated database session (function-scoped)."""
    async with AsyncSession(test_engine, expire_on_commit=False) as session:
        async with session.begin():
            yield session
            await session.rollback()  # Rollback transaction (clean slate for next test)
```

**Benefits:**
- ✅ **Test isolation** - Each test starts with clean database
- ✅ **Performance** - Schema created once per session
- ✅ **Debugging** - SQL logs show exact queries
- ✅ **Reliability** - No test interdependencies

---

#### Strategy 2: Seed Data for Manual Testing

**Purpose:** Populate development/test database with realistic data for manual exploration and E2E testing.

```python
# backend/scripts/seed_data.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.database import Base
from app.models.project import Project
from app.models.project_doc import ProjectDoc
from app.models.llm_provider import LLMProvider
from app.config import get_settings

settings = get_settings()

async def seed_test_data():
    """Seed test database with realistic data."""
    engine = create_async_engine(settings.DATABASE_URL)

    async with AsyncSession(engine) as session:
        # Create test projects
        projects = [
            Project(
                name="AgentLab Documentation",
                description="AI agent framework for Claude Code integration"
            ),
            Project(
                name="Magnet Framework",
                description="Pattern library for BMAD Method development"
            ),
            Project(
                name="BMADFlow (Self)",
                description="This documentation hub itself"
            )
        ]
        session.add_all(projects)
        await session.commit()

        # Create test ProjectDocs
        docs = [
            ProjectDoc(
                project_id=projects[0].id,
                name="AgentLab PRD",
                github_url="https://github.com/example/agentlab",
                github_folder_path="docs",
                description="Product requirements and architecture"
            ),
            ProjectDoc(
                project_id=projects[0].id,
                name="AgentLab User Stories",
                github_url="https://github.com/example/agentlab",
                github_folder_path="docs/stories",
                description="Development stories and tasks"
            ),
            ProjectDoc(
                project_id=projects[1].id,
                name="Magnet Patterns",
                github_url="https://github.com/example/magnet",
                github_folder_path="patterns",
                description="Reusable development patterns"
            )
        ]
        session.add_all(docs)
        await session.commit()

        # Create default LLM providers
        providers = [
            LLMProvider(
                provider_name="ollama",
                model_name="llama2",
                is_default=True,
                api_config={"endpoint": "http://localhost:11434"}
            ),
            LLMProvider(
                provider_name="openai",
                model_name="gpt-4",
                is_default=False,
                api_config={"temperature": 0.7}
            )
        ]
        session.add_all(providers)
        await session.commit()

        print("✅ Seed complete:")
        print(f"  - {len(projects)} projects")
        print(f"  - {len(docs)} ProjectDocs")
        print(f"  - {len(providers)} LLM providers")

if __name__ == "__main__":
    asyncio.run(seed_test_data())
```

**Usage:**

```bash
# Seed development database
python backend/scripts/seed_data.py

# Seed test database (for manual E2E testing)
DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/bmadflow_test \
  python backend/scripts/seed_data.py
```

---

#### Strategy 3: Mock Data Factories (Frontend)

**Purpose:** Generate realistic test data for component tests using faker.

```typescript
// frontend/tests/fixtures/factories.ts
import { faker } from '@faker-js/faker';
import { Project, ProjectDoc, Conversation, Message } from '@/types';

export class ProjectFactory {
  /**
   * Create a mock Project with realistic data.
   */
  static create(overrides?: Partial<Project>): Project {
    return {
      id: faker.string.uuid(),
      name: faker.company.name(),
      description: faker.lorem.sentence(),
      created_at: faker.date.past().toISOString(),
      updated_at: faker.date.recent().toISOString(),
      ...overrides
    };
  }

  /**
   * Create multiple mock Projects.
   */
  static createMany(count: number, overrides?: Partial<Project>): Project[] {
    return Array.from({ length: count }, () => this.create(overrides));
  }
}

export class ProjectDocFactory {
  /**
   * Create a mock ProjectDoc.
   */
  static create(projectId: string, overrides?: Partial<ProjectDoc>): ProjectDoc {
    return {
      id: faker.string.uuid(),
      project_id: projectId,
      name: `${faker.hacker.noun()} Documentation`,
      description: faker.lorem.paragraph(),
      github_url: `https://github.com/${faker.internet.userName()}/${faker.lorem.word()}`,
      github_folder_path: 'docs',
      last_synced_at: faker.date.recent().toISOString(),
      last_github_commit_date: faker.date.recent().toISOString(),
      created_at: faker.date.past().toISOString(),
      updated_at: faker.date.recent().toISOString(),
      ...overrides
    };
  }
}

export class ConversationFactory {
  /**
   * Create a mock Conversation with messages.
   */
  static create(projectId: string, overrides?: Partial<Conversation>): Conversation {
    const messages: Message[] = [
      {
        id: faker.string.uuid(),
        role: 'user',
        content: faker.lorem.question(),
        created_at: faker.date.recent().toISOString()
      },
      {
        id: faker.string.uuid(),
        role: 'assistant',
        content: faker.lorem.paragraph(),
        sources: [
          {
            document_id: faker.string.uuid(),
            file_path: 'docs/prd.md',
            header_anchor: 'requirements'
          },
          {
            document_id: faker.string.uuid(),
            file_path: 'docs/architecture.md',
            header_anchor: 'database-schema'
          }
        ],
        created_at: faker.date.recent().toISOString()
      }
    ];

    return {
      id: faker.string.uuid(),
      project_id: projectId,
      title: faker.lorem.sentence(),
      messages,
      created_at: faker.date.past().toISOString(),
      updated_at: faker.date.recent().toISOString(),
      ...overrides
    };
  }
}
```

**Usage in Component Tests:**

```typescript
// tests/components/ProjectCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ProjectCard } from '@/components/ProjectCard';
import { ProjectFactory } from '../fixtures/factories';

describe('ProjectCard', () => {
  it('renders project with description', () => {
    // Arrange - Use factory for clean test data
    const project = ProjectFactory.create({
      name: 'BMAD Documentation',
      description: 'Central hub for all BMAD projects'
    });

    // Act
    render(<ProjectCard project={project} />);

    // Assert
    expect(screen.getByText('BMAD Documentation')).toBeInTheDocument();
    expect(screen.getByText('Central hub for all BMAD projects')).toBeInTheDocument();
  });

  it('renders multiple project cards', () => {
    const projects = ProjectFactory.createMany(3);

    render(
      <div>
        {projects.map(project => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
    );

    expect(screen.getAllByRole('article')).toHaveLength(3);
  });
});
```

---

#### Strategy 4: E2E Test Data Setup

**Playwright Test Fixtures for Data Setup/Teardown:**

```typescript
// frontend/tests/e2e/setup/test-data.ts
import { test as base } from '@playwright/test';
import { Project, ProjectDoc } from '@/types';

type TestFixtures = {
  authenticatedProject: Project;
  syncedProjectDoc: ProjectDoc;
};

export const test = base.extend<TestFixtures>({
  /**
   * Fixture: Create test project via API.
   */
  authenticatedProject: async ({ page }, use) => {
    // Setup: Create project
    const response = await page.request.post('http://localhost:8000/api/projects', {
      data: {
        name: 'E2E Test Project',
        description: 'Automated test project for E2E validation'
      }
    });
    const project = await response.json();

    // Provide to test
    await use(project);

    // Teardown: Delete project
    await page.request.delete(`http://localhost:8000/api/projects/${project.id}`);
  },

  /**
   * Fixture: Create and sync ProjectDoc.
   */
  syncedProjectDoc: async ({ authenticatedProject, page }, use) => {
    // Setup: Create ProjectDoc
    const docResponse = await page.request.post(
      `http://localhost:8000/api/projects/${authenticatedProject.id}/docs`,
      {
        data: {
          name: 'Test Documentation',
          github_url: 'https://github.com/test/repo',
          github_folder_path: 'docs',
          description: 'Test docs for E2E'
        }
      }
    );
    const doc = await docResponse.json();

    // Trigger sync (wait for completion)
    const syncResponse = await page.request.post(
      `http://localhost:8000/api/project-docs/${doc.id}/sync`
    );
    await syncResponse.json();

    // Provide synced doc to test
    await use(doc);

    // Teardown: Auto-deleted via project cascade
  }
});
```

**E2E Test Using Fixtures:**

```typescript
// tests/e2e/browse-documentation.spec.ts
import { test } from './setup/test-data';
import { expect } from '@playwright/test';

test.describe('Browse Documentation', () => {
  test('navigates synced documentation', async ({ page, syncedProjectDoc }) => {
    // Given: Data already synced via fixture
    const projectId = syncedProjectDoc.project_id;

    // When: Navigate to Explorer
    await page.goto(`http://localhost:3000/projects/${projectId}/explorer`);

    // Then: File tree loads
    await expect(page.locator('[data-testid="file-tree"]')).toBeVisible();

    // And: Files are listed
    await expect(page.locator('[data-testid="file-item"]')).toHaveCount(await page.locator('[data-testid="file-item"]').count());
  });
});
```

---

### Layer 4: Test Infrastructure Setup

#### Backend Test Environment

**File: backend/requirements-test.txt**
```
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
httpx==0.25.2              # AsyncClient for API tests
faker==20.1.0              # Test data generation
freezegun==1.4.0           # Time mocking
```

**File: backend/pytest.ini**
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v                      # Verbose output
    --strict-markers        # Fail on unknown markers
    --cov=app               # Coverage for app/ directory
    --cov-report=html       # HTML coverage report
    --cov-report=term       # Terminal summary
    --cov-fail-under=70     # Enforce 70% coverage (NFR18)
```

**File: backend/.env.test**
```bash
# Test database
DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/bmadflow_test

# Mock external services
OLLAMA_ENDPOINT_URL=http://mock-ollama:11434
OPENAI_API_KEY=test-key-not-used
GOOGLE_API_KEY=test-key-not-used

# Test server port
BACKEND_PORT=8001
```

**Setup Commands:**
```bash
# Create test database
docker exec -it bmadflow-postgres psql -U postgres -c "CREATE DATABASE bmadflow_test;"

# Install test dependencies
cd backend
pip install -r requirements-test.txt

# Run tests with coverage
pytest

# View HTML coverage report
open htmlcov/index.html
```

---

#### Frontend Test Environment

**File: frontend/package.json (test dependencies)**
```json
{
  "devDependencies": {
    "vitest": "^1.0.4",
    "@testing-library/react": "^14.1.2",
    "@testing-library/user-event": "^14.5.1",
    "@testing-library/jest-dom": "^6.1.5",
    "@playwright/test": "^1.40.1",
    "@faker-js/faker": "^8.3.1",
    "msw": "^2.0.11"
  }
}
```

**File: frontend/vitest.config.ts**
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.config.ts',
        '**/*.d.ts'
      ],
      thresholds: {
        lines: 60,
        functions: 60,
        branches: 60,
        statements: 60
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
```

**File: frontend/tests/setup.ts**
```typescript
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
```

**Setup Commands:**
```bash
cd frontend
npm install

# Run component tests
npm test

# Run with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e

# Run E2E in UI mode
npx playwright test --ui
```

---

### Layer 5: Testing Best Practices

#### Best Practice 1: Test Naming Convention

```python
# Good: Descriptive test names
def test_create_project_with_valid_data_returns_201():
    """Test that creating a project with valid data returns 201 Created."""
    pass

def test_create_project_without_name_returns_422():
    """Test that creating a project without name returns 422 Validation Error."""
    pass

# Bad: Vague test names
def test_create_project():
    pass

def test_project():
    pass
```

#### Best Practice 2: Arrange-Act-Assert (AAA) Pattern

```python
@pytest.mark.asyncio
async def test_sync_updates_last_synced_timestamp(db_session):
    # Arrange - Setup test data
    project = await ProjectBuilder().build(db_session)
    doc = await ProjectDocBuilder().for_project(project.id).build(db_session)

    # Act - Execute operation
    await sync_service.sync_project_doc(doc.id)

    # Assert - Verify results
    await db_session.refresh(doc)
    assert doc.last_synced_at is not None
    assert doc.last_synced_at > doc.created_at
```

#### Best Practice 3: Test One Thing Per Test

```python
# Good: Single responsibility
@pytest.mark.asyncio
async def test_create_project_returns_correct_name(client):
    response = await client.post("/api/projects", json={"name": "Test"})
    assert response.json()["name"] == "Test"

@pytest.mark.asyncio
async def test_create_project_generates_uuid(client):
    response = await client.post("/api/projects", json={"name": "Test"})
    assert UUID(response.json()["id"])  # Valid UUID

# Bad: Multiple assertions testing different things
@pytest.mark.asyncio
async def test_create_project(client):
    response = await client.post("/api/projects", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
    assert UUID(response.json()["id"])
    assert response.json()["created_at"] is not None
```

#### Best Practice 4: Use Fixtures for Reusable Setup

```python
# conftest.py - Shared fixtures
@pytest.fixture
async def test_project(db_session):
    """Provide a test project."""
    return await ProjectBuilder().build(db_session)

@pytest.fixture
async def synced_project_doc(db_session, test_project):
    """Provide a synced ProjectDoc."""
    doc = await ProjectDocBuilder() \
        .for_project(test_project.id) \
        .build(db_session)
    await sync_service.sync_project_doc(doc.id)
    return doc

# Usage - Clean test code
@pytest.mark.asyncio
async def test_query_synced_docs(synced_project_doc):
    """Test querying embeddings from synced docs."""
    results = await vector_search("test query", synced_project_doc.project_id)
    assert len(results) > 0
```

#### Best Practice 5: Mock External APIs Consistently

```python
# Create reusable mock fixtures
@pytest.fixture
def mock_github_api():
    """Mock GitHub API responses."""
    with patch("app.services.github_service.httpx.AsyncClient") as mock:
        mock.get.return_value.json.return_value = {
            "tree": [{"path": "README.md", "type": "blob"}]
        }
        mock.get.return_value.headers = {"X-RateLimit-Remaining": "59"}
        yield mock

@pytest.fixture
def mock_ollama_embeddings():
    """Mock Ollama embedding generation."""
    with patch("app.services.embedding_service.ollama") as mock:
        mock.embeddings.return_value = {"embedding": [0.1] * 768}
        yield mock
```

---

## Implementation Roadmap

### Phase 1: Foundation (Epic 1)
**Story 1.1-1.3: Test Infrastructure Setup**
- ✅ Create test directory structure
- ✅ Configure pytest + vitest
- ✅ Setup test database with fixtures
- ✅ Configure coverage reporting
- ✅ Write first RED-GREEN-REFACTOR test

### Phase 2: Core Testing (Epic 2-3)
**Story 2.1-2.7: API & Integration Tests**
- ✅ Unit tests for services/repositories
- ✅ Integration tests for API endpoints
- ✅ Mock GitHub/Ollama services
- ✅ Test data builders for complex objects

### Phase 3: Component Testing (Epic 3)
**Story 3.1-3.7: Frontend Component Tests**
- ✅ React component tests with Testing Library
- ✅ Mock API responses with MSW
- ✅ Hook tests for custom hooks
- ✅ Visual regression baselines

### Phase 4: E2E Testing (Epic 4-5)
**Story 4.6 & 5.6: Playwright E2E Tests**
- ✅ Critical flow tests (Browse, Sync, Chat)
- ✅ Playwright MCP integration
- ✅ Screenshot baselines
- ✅ Performance validation

### Phase 5: Quality Gates (Before Release)
**Comprehensive Quality Validation**
- ✅ Execute full test suite
- ✅ Validate 70% backend coverage
- ✅ Run visual regression tests
- ✅ Performance benchmark validation

---

## Success Metrics

### Coverage Metrics (NFR18)
- ✅ **Backend:** 70%+ for services, repositories, utils
- ✅ **Frontend:** 60%+ for components, hooks
- ✅ **E2E:** 100% critical path coverage

### Quality Metrics
- ✅ **Test execution time:** <5min for unit/integration, <10min for E2E
- ✅ **Test reliability:** <1% flakiness rate
- ✅ **Code review:** No PR merged without tests
- ✅ **Coverage enforcement:** CI fails if coverage drops

### Process Metrics
- ✅ **Test-first adoption:** 100% of stories
- ✅ **Bug escape rate:** <5% to production
- ✅ **Refactoring confidence:** Tests pass after refactor
- ✅ **Debug time:** <30min from failure to root cause

---

## Related Documentation

- **Playwright MCP E2E Strategy:** [docs/qa/playwright-mcp-e2e-strategy.md](./playwright-mcp-e2e-strategy.md)
- **Testing Strategy:** [docs/architecture/testing-strategy.md](../architecture/testing-strategy.md)
- **PRD Testing Requirements:** [docs/prd.md#testing-requirements](../prd.md)
- **Architecture Testability Review:** [docs/qa/architecture-testability-review.md](./architecture-testability-review.md)

---

**Document Status:** ✅ Approved for Implementation
**Next Action:** Execute Phase 1 - Test Infrastructure Setup (Story 1.1)
