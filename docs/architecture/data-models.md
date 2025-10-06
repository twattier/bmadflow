# Data Models

## Overview

BMADFlow uses **SQLAlchemy 2.x** ORM models for database access and **Pydantic 2.x** models for API request/response validation. This dual-model approach provides:

- **SQLAlchemy Models**: Database entities with relationships, mapped to PostgreSQL tables
- **Pydantic Models**: Type-safe API contracts with automatic validation and OpenAPI schema generation
- **Shared Types**: TypeScript type generation from Pydantic models for frontend type safety

**Design Principles:**
- **Async-First**: All SQLAlchemy models use async sessions (AsyncSession)
- **Validation at Boundaries**: Pydantic validates all API inputs/outputs
- **Type Safety**: End-to-end type safety from database → API → frontend
- **Separation of Concerns**: Database models separate from API models (DTO pattern)

## SQLAlchemy Models (Database Entities)

All models inherit from `Base` (declarative_base) and use async-compatible patterns.

### Base Configuration

```python
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, func
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass
```

---

### 1. Project Model

```python
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import uuid
from datetime import datetime

class Project(Base):
    __tablename__ = "projects"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    # Attributes
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    project_docs: Mapped[List["ProjectDoc"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"
```

---

### 2. ProjectDoc Model

```python
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

class ProjectDoc(Base):
    __tablename__ = "project_docs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_url: Mapped[str] = mapped_column(String(512), nullable=False)
    github_folder_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_github_commit_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="project_docs")
    documents: Mapped[List["Document"]] = relationship(
        back_populates="project_doc",
        cascade="all, delete-orphan"
    )
```

---

### 3. Document Model

```python
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_doc_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("project_docs.id", ondelete="CASCADE"),
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    project_doc: Mapped["ProjectDoc"] = relationship(back_populates="documents")
    chunks: Mapped[List["Chunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("project_doc_id", "file_path", name="uq_project_doc_file_path"),
    )
```

---

### 4. Chunk Model (Vector Embeddings)

```python
from pgvector.sqlalchemy import Vector

class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[Vector] = mapped_column(Vector(768), nullable=False)  # nomic-embed-text
    header_anchor: Mapped[str | None] = mapped_column(String(512), nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    document: Mapped["Document"] = relationship(back_populates="chunks")

    # Indexes created in migration
    __table_args__ = (
        Index("idx_document_chunk", "document_id", "chunk_index"),
    )
```

---

### 5. LLMProvider Model

```python
from sqlalchemy import String, Boolean

class LLMProvider(Base):
    __tablename__ = "llm_providers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    api_config: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    conversations: Mapped[List["Conversation"]] = relationship(
        back_populates="llm_provider"
    )

    __table_args__ = (
        UniqueConstraint("provider_name", "model_name", name="uq_provider_model"),
    )
```

---

### 6. Conversation Model

```python
class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    llm_provider_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("llm_providers.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="conversations")
    llm_provider: Mapped["LLMProvider"] = relationship(back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
```

---

### 7. Message Model

```python
from sqlalchemy import CheckConstraint

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="ck_message_role"),
    )
```

---

## Pydantic Models (API DTOs)

Pydantic models define request/response schemas with automatic validation.

### Request Models (Create/Update)

```python
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime
import uuid

class ProjectCreate(BaseModel):
    """Request model for creating a project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None

class ProjectUpdate(BaseModel):
    """Request model for updating a project."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None

class ProjectDocCreate(BaseModel):
    """Request model for creating a project doc."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    github_url: HttpUrl
    github_folder_path: str | None = None

class ConversationCreate(BaseModel):
    """Request model for creating a conversation."""
    llm_provider_id: uuid.UUID
    title: str | None = Field(None, max_length=255)

class MessageCreate(BaseModel):
    """Request model for sending a message."""
    content: str = Field(..., min_length=1)
```

---

### Response Models (Read)

```python
from typing import List

class ProjectResponse(BaseModel):
    """Response model for project data."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

class ProjectDocResponse(BaseModel):
    """Response model for project doc data."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: str | None
    github_url: str
    github_folder_path: str | None
    last_synced_at: datetime | None
    last_github_commit_date: datetime | None
    created_at: datetime
    updated_at: datetime

class DocumentResponse(BaseModel):
    """Response model for document metadata."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_doc_id: uuid.UUID
    file_path: str
    file_type: str
    file_size: int
    metadata: dict | None
    created_at: datetime
    updated_at: datetime

class ChunkSearchResult(BaseModel):
    """Response model for vector search results."""
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    chunk_text: str
    header_anchor: str | None
    similarity_score: float
    file_path: str

class MessageResponse(BaseModel):
    """Response model for chat messages."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    sources: List[dict] | None
    created_at: datetime

class ConversationResponse(BaseModel):
    """Response model for conversation with messages."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    llm_provider_id: uuid.UUID
    title: str
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime
```

---

## Type Generation for Frontend

**Strategy**: Use `pydantic-to-typescript` or similar tool to generate TypeScript interfaces from Pydantic models.

**Generated TypeScript Example**:
```typescript
// Generated from Pydantic models
export interface ProjectResponse {
  id: string;  // UUID
  name: string;
  description: string | null;
  created_at: string;  // ISO datetime
  updated_at: string;
}

export interface MessageCreate {
  content: string;
}

export interface ChunkSearchResult {
  chunk_id: string;
  document_id: string;
  chunk_text: string;
  header_anchor: string | null;
  similarity_score: number;
  file_path: string;
}
```

**Build Step**: Add to CI/CD or pre-commit hook to regenerate TypeScript types when Pydantic models change.

---

## Model Validation Examples

### Pydantic Field Validators

```python
from pydantic import field_validator

class ProjectDocCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    github_url: HttpUrl
    github_folder_path: str | None = None

    @field_validator('github_url')
    @classmethod
    def validate_github_url(cls, v: HttpUrl) -> HttpUrl:
        """Ensure URL is from github.com."""
        if v.host not in ['github.com', 'www.github.com']:
            raise ValueError('Must be a GitHub repository URL')
        return v

    @field_validator('github_folder_path')
    @classmethod
    def validate_folder_path(cls, v: str | None) -> str | None:
        """Normalize folder path."""
        if v is None:
            return v
        # Remove leading/trailing slashes
        return v.strip('/')
```

---

## Database Session Management

**Async Session Dependency** (for FastAPI):

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator

# Engine configuration
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async with AsyncSessionLocal() as session:
        yield session
```

**Usage in FastAPI Route**:
```python
@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

---

## Model Conversion Patterns

### SQLAlchemy → Pydantic

```python
# Automatic conversion with from_attributes=True
project_db = await get_project_from_db(project_id)
return ProjectResponse.model_validate(project_db)
```

### Pydantic → SQLAlchemy

```python
# Create new entity from request
project_create = ProjectCreate(name="My Project", description="Description")
project_db = Project(**project_create.model_dump())
db.add(project_db)
await db.commit()
```

---

## Related Documentation

- **Database Schema**: See [Database Schema](#database-schema) section for table definitions
- **API Endpoints**: See [API Specification](#api-specification) section for endpoint details
- **Implementation Patterns**: [FastAPI Patterns](context/backend/fastapi-patterns.md) for dependency injection and async patterns

---
