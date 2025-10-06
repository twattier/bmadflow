# FastAPI Backend Patterns

This document provides essential FastAPI patterns and code examples for BMADFlow backend development.

## Async API Routes

FastAPI uses async/await for non-blocking I/O operations, essential for database queries and external API calls.

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Async route with database dependency injection."""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

## Dependency Injection

FastAPI's dependency injection system manages database sessions, authentication, and shared services.

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Database session dependency
async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=True
)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """Database session dependency."""
    async with AsyncSessionLocal() as session:
        yield session
```

## Pydantic Models for Request/Response

Pydantic models provide automatic validation, serialization, and OpenAPI documentation.

```python
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional

class ProjectCreate(BaseModel):
    """Request model for creating a project."""
    name: str = Field(..., min_length=1, max_length=255)
    repo_url: HttpUrl
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    """Response model for project data."""
    id: int
    name: str
    repo_url: str
    description: Optional[str]
    created_at: datetime
    last_synced_at: Optional[datetime]

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models
```

## Error Handling

Consistent error responses using HTTPException and custom exception handlers.

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class ProjectNotFoundError(Exception):
    def __init__(self, project_id: int):
        self.project_id = project_id

@app.exception_handler(ProjectNotFoundError)
async def project_not_found_handler(request: Request, exc: ProjectNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Project {exc.project_id} not found",
            "error_code": "PROJECT_NOT_FOUND"
        }
    )
```

## Background Tasks

FastAPI background tasks for long-running operations like GitHub synchronization.

```python
from fastapi import BackgroundTasks

def sync_github_repo(project_id: int, repo_url: str):
    """Background task for syncing GitHub repository."""
    # Long-running sync logic here
    pass

@app.post("/projects/{project_id}/sync")
async def trigger_sync(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger GitHub sync as background task."""
    project = await get_project_or_404(db, project_id)
    background_tasks.add_task(sync_github_repo, project.id, project.repo_url)
    return {"message": "Sync started", "project_id": project_id}
```

## OpenAPI/Swagger Configuration

FastAPI automatically generates OpenAPI documentation, customizable for better API exploration.

```python
from fastapi import FastAPI

app = FastAPI(
    title="BMADFlow API",
    description="Documentation hub with RAG chatbot for BMAD Method projects",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Tags for grouping endpoints
tags_metadata = [
    {"name": "projects", "description": "Project management operations"},
    {"name": "documents", "description": "Document retrieval and metadata"},
    {"name": "chat", "description": "RAG chatbot endpoints"},
]

app = FastAPI(openapi_tags=tags_metadata)
```

## Repository Pattern

Abstract database access behind repository interfaces for testability.

```python
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_id: int) -> Optional[Project]:
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> List[Project]:
        result = await self.db.execute(select(Project))
        return result.scalars().all()

    async def create(self, project_data: ProjectCreate) -> Project:
        project = Project(**project_data.model_dump())
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project
```

## CORS Configuration

Enable CORS for frontend communication during development and production.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Related Documentation

- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [PostgreSQL Integration](/docs/context/database/postgresql-patterns.md)
- [Architecture Overview](/docs/architecture.md#backend-architecture)
