# PostgreSQL + pgvector Patterns for RAG Applications

## Overview

This document provides comprehensive patterns and best practices for using PostgreSQL with pgvector extension for Retrieval-Augmented Generation (RAG) applications. All examples are optimized for 768-dimensional embeddings, a common dimension for modern embedding models.

## Table of Contents

1. [Setup and Configuration](#setup-and-configuration)
2. [SQLAlchemy 2.x Async Integration](#sqlalchemy-2x-async-integration)
3. [Vector Storage and Indexing](#vector-storage-and-indexing)
4. [Query Patterns](#query-patterns)
5. [Performance Optimization](#performance-optimization)
6. [Connection Pooling](#connection-pooling)
7. [Best Practices](#best-practices)

---

## Setup and Configuration

### Enable pgvector Extension

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### SQLAlchemy Model Definition

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column
from pgvector.sqlalchemy import Vector
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = "documents"

    id = mapped_column(Integer, primary_key=True)
    content = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(768), nullable=False)
    metadata_ = mapped_column(Text)  # JSON or additional metadata
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Alternative: Add Vector Column to Existing Table

```python
from sqlalchemy import text

async with engine.begin() as conn:
    await conn.execute(text(
        "ALTER TABLE documents ADD COLUMN embedding vector(768)"
    ))
```

---

## SQLAlchemy 2.x Async Integration

### Engine Creation with asyncpg

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool

# Production configuration with connection pooling
engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost:5432/dbname",
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,  # Number of connections to maintain
    max_overflow=5,  # Additional connections when pool is exhausted
    pool_timeout=30,  # Seconds to wait for a connection
    poolclass=AsyncAdaptedQueuePool,  # Default for async engines
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### Alternative: Psycopg3 (Async)

```python
from sqlalchemy.ext.asyncio import create_async_engine
from pgvector.psycopg import register_vector_async
from sqlalchemy import event

# Create engine
engine = create_async_engine(
    "postgresql+psycopg://user:password@localhost:5432/dbname",
    pool_pre_ping=True,
)

# Register vector type for psycopg
@event.listens_for(engine.sync_engine, "connect")
def connect(dbapi_connection, connection_record):
    dbapi_connection.run_async(register_vector_async)
```

### Register Vector Type with asyncpg

```python
from pgvector.asyncpg import register_vector
from sqlalchemy import event

@event.listens_for(engine.sync_engine, "connect")
async def register_asyncpg_vector(dbapi_connection, connection_record):
    await register_vector(dbapi_connection)
```

### Basic Async Operations

```python
from sqlalchemy import select
import numpy as np

async def insert_document(session: AsyncSession, content: str, embedding: np.ndarray):
    """Insert a document with its embedding."""
    doc = Document(
        content=content,
        embedding=embedding.tolist()  # Convert numpy array to list
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc

async def get_document_by_id(session: AsyncSession, doc_id: int):
    """Retrieve a document by ID."""
    result = await session.execute(
        select(Document).where(Document.id == doc_id)
    )
    return result.scalar_one_or_none()
```

### Context Manager Pattern

```python
async def example_usage():
    """Recommended pattern for async operations."""
    async with async_session() as session:
        async with session.begin():
            # Insert operations
            doc = Document(
                content="Sample text",
                embedding=[0.1] * 768
            )
            session.add(doc)
        # Commit happens automatically at end of begin() block

    # Query operations (read-only)
    async with async_session() as session:
        result = await session.execute(
            select(Document).limit(10)
        )
        documents = result.scalars().all()
```

---

## Vector Storage and Indexing

### Distance Functions

pgvector supports multiple distance functions:

| Operator | Distance Type | Use Case |
|----------|---------------|----------|
| `<->` | L2 (Euclidean) | General purpose, magnitude-sensitive |
| `<=>` | Cosine Distance | Normalized embeddings, direction-focused |
| `<#>` | Negative Inner Product | Dot product similarity (multiply by -1) |
| `<+>` | L1 (Manhattan) | Sparse vectors, dimension independence |

```python
from sqlalchemy import select

async def find_similar_l2(session: AsyncSession, query_embedding: list, limit: int = 5):
    """Find similar documents using L2 distance."""
    result = await session.execute(
        select(Document)
        .order_by(Document.embedding.l2_distance(query_embedding))
        .limit(limit)
    )
    return result.scalars().all()

async def find_similar_cosine(session: AsyncSession, query_embedding: list, limit: int = 5):
    """Find similar documents using cosine distance."""
    result = await session.execute(
        select(Document)
        .order_by(Document.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    return result.scalars().all()
```

### Index Strategies

#### HNSW Index (Recommended for Production)

HNSW (Hierarchical Navigable Small World) provides excellent recall with fast queries:

```python
from sqlalchemy import Index, text

# Create HNSW index with L2 distance
hnsw_l2_index = Index(
    'documents_embedding_hnsw_l2_idx',
    Document.embedding,
    postgresql_using='hnsw',
    postgresql_with={'m': 16, 'ef_construction': 64},
    postgresql_ops={'embedding': 'vector_l2_ops'}
)

# Create HNSW index with cosine distance
hnsw_cosine_index = Index(
    'documents_embedding_hnsw_cosine_idx',
    Document.embedding,
    postgresql_using='hnsw',
    postgresql_with={'m': 16, 'ef_construction': 64},
    postgresql_ops={'embedding': 'vector_cosine_ops'}
)

# Create index
async with engine.begin() as conn:
    await conn.run_sync(hnsw_l2_index.create)
```

**HNSW Parameters:**
- `m`: Number of connections per layer (default: 16)
  - Higher values = better recall, more memory
  - Recommended: 12-48 for 768 dimensions
- `ef_construction`: Size of candidate list during index build (default: 64)
  - Higher values = better quality, slower build
  - Recommended: 64-200 for production

**Runtime Configuration:**

```python
from sqlalchemy import text

async def configure_hnsw_search(session: AsyncSession, ef_search: int = 100):
    """Configure HNSW search parameters for better recall."""
    await session.execute(text(f"SET hnsw.ef_search = {ef_search}"))
    # Higher ef_search = better recall, slower queries
    # Default: 40, Recommended for RAG: 100-200
```

#### IVFFlat Index (Alternative)

IVFFlat is faster to build but requires more tuning:

```python
# Create IVFFlat index
ivfflat_index = Index(
    'documents_embedding_ivfflat_idx',
    Document.embedding,
    postgresql_using='ivfflat',
    postgresql_with={'lists': 100},  # Number of clusters
    postgresql_ops={'embedding': 'vector_l2_ops'}
)

# Lists parameter calculation:
# For 1M rows: lists = rows / 1000 ≈ 1000
# For 100K rows: lists = sqrt(rows) ≈ 316
```

**Runtime Configuration:**

```python
async def configure_ivfflat_probes(session: AsyncSession, probes: int = 10):
    """Configure IVFFlat search probes."""
    await session.execute(text(f"SET ivfflat.probes = {probes}"))
    # Higher probes = better recall, slower queries
    # Default: 1, Recommended: 10-20
```

#### Partial Indexes for Filtered Queries

```python
# Index only specific document types
filtered_index = Index(
    'documents_embedding_type_filtered_idx',
    Document.embedding,
    postgresql_using='hnsw',
    postgresql_with={'m': 16, 'ef_construction': 64},
    postgresql_ops={'embedding': 'vector_l2_ops'},
    postgresql_where=text("metadata_->>'type' = 'article'")
)
```

### Index Build Optimization

```python
from sqlalchemy import text

async def optimize_index_build(session: AsyncSession):
    """Configure PostgreSQL for faster index builds."""
    # Increase maintenance work memory
    await session.execute(text("SET maintenance_work_mem = '2GB'"))

    # Enable parallel workers
    await session.execute(text("SET max_parallel_maintenance_workers = 7"))

    # Create index concurrently (allows writes during build)
    await session.execute(text(
        "CREATE INDEX CONCURRENTLY documents_embedding_hnsw_idx "
        "ON documents USING hnsw (embedding vector_l2_ops) "
        "WITH (m = 16, ef_construction = 64)"
    ))
```

### Monitor Index Build Progress

```python
async def check_index_progress(session: AsyncSession):
    """Monitor index creation progress."""
    result = await session.execute(text(
        "SELECT phase, "
        "round(100.0 * tuples_done / NULLIF(tuples_total, 0), 1) AS percent "
        "FROM pg_stat_progress_create_index"
    ))
    return result.fetchone()
```

---

## Query Patterns

### Basic Similarity Search

```python
from sqlalchemy import select, func

async def semantic_search(
    session: AsyncSession,
    query_embedding: list,
    limit: int = 5,
    distance_threshold: float = None
):
    """
    Perform semantic search with optional distance filtering.

    Args:
        session: AsyncSession instance
        query_embedding: Query vector (768 dimensions)
        limit: Maximum number of results
        distance_threshold: Optional maximum distance
    """
    query = select(
        Document,
        Document.embedding.l2_distance(query_embedding).label('distance')
    ).order_by(
        Document.embedding.l2_distance(query_embedding)
    )

    if distance_threshold is not None:
        query = query.filter(
            Document.embedding.l2_distance(query_embedding) < distance_threshold
        )

    query = query.limit(limit)

    result = await session.execute(query)
    return result.all()
```

### Filtered Similarity Search

```python
async def filtered_semantic_search(
    session: AsyncSession,
    query_embedding: list,
    metadata_filter: dict,
    limit: int = 5
):
    """
    Similarity search with metadata filtering.

    Important: Create appropriate B-tree indexes on filter columns:
    CREATE INDEX ON documents (metadata_->>'category');
    """
    from sqlalchemy.dialects.postgresql import JSONB

    query = select(Document).where(
        Document.metadata_['category'].astext == metadata_filter.get('category')
    ).order_by(
        Document.embedding.l2_distance(query_embedding)
    ).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()
```

### Hybrid Search (Vector + Full-Text)

```python
from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import TSVECTOR

# First, add a tsvector column
async def setup_fulltext_search(session: AsyncSession):
    """Setup full-text search capabilities."""
    await session.execute(text(
        "ALTER TABLE documents ADD COLUMN content_tsv tsvector "
        "GENERATED ALWAYS AS (to_tsvector('english', content)) STORED"
    ))
    await session.execute(text(
        "CREATE INDEX documents_content_tsv_idx ON documents USING GIN(content_tsv)"
    ))

async def hybrid_search(
    session: AsyncSession,
    query_embedding: list,
    query_text: str,
    vector_weight: float = 0.7,
    text_weight: float = 0.3,
    limit: int = 5
):
    """
    Combine vector similarity with full-text search.

    Uses Reciprocal Rank Fusion (RRF) for combining results.
    """
    # Vector search subquery
    vector_query = select(
        Document.id,
        Document.embedding.l2_distance(query_embedding).label('vec_distance')
    ).order_by(
        Document.embedding.l2_distance(query_embedding)
    ).limit(20).subquery()

    # Full-text search subquery
    text_query = select(
        Document.id,
        func.ts_rank(Document.content_tsv, func.plainto_tsquery('english', query_text)).label('text_rank')
    ).where(
        Document.content_tsv.op('@@')(func.plainto_tsquery('english', query_text))
    ).order_by(
        func.ts_rank(Document.content_tsv, func.plainto_tsquery('english', query_text)).desc()
    ).limit(20).subquery()

    # Combine using RRF
    combined = select(
        Document,
        (
            vector_weight / (60 + func.coalesce(vector_query.c.vec_distance, 1000)) +
            text_weight / (60 + func.coalesce(text_query.c.text_rank, 0))
        ).label('combined_score')
    ).select_from(Document).outerjoin(
        vector_query, Document.id == vector_query.c.id
    ).outerjoin(
        text_query, Document.id == text_query.c.id
    ).where(
        (vector_query.c.id.isnot(None)) | (text_query.c.id.isnot(None))
    ).order_by(
        text('combined_score DESC')
    ).limit(limit)

    result = await session.execute(combined)
    return result.all()
```

### Batch Insert with COPY

```python
import io
import struct

async def bulk_insert_embeddings(
    session: AsyncSession,
    documents: list[tuple[str, list[float]]]
):
    """
    Efficiently insert large numbers of documents using COPY.

    Args:
        documents: List of (content, embedding) tuples
    """
    from sqlalchemy import text

    # Prepare binary data
    buffer = io.BytesIO()

    for content, embedding in documents:
        # Convert to pgvector binary format
        # Format: dimension (int16), then float32 values
        dim = len(embedding)
        buffer.write(struct.pack('>H', dim))  # dimensions as big-endian uint16
        for val in embedding:
            buffer.write(struct.pack('>f', val))  # values as big-endian float32

    buffer.seek(0)

    # Use raw connection for COPY
    raw_conn = await session.connection()
    cursor = await raw_conn.get_raw_connection().cursor()

    await cursor.copy_expert(
        "COPY documents (content, embedding) FROM STDIN WITH (FORMAT BINARY)",
        buffer
    )
```

### Aggregate Operations

```python
async def compute_centroid(session: AsyncSession, doc_ids: list[int]):
    """Compute the average embedding (centroid) of a set of documents."""
    from pgvector.sqlalchemy import avg

    result = await session.execute(
        select(avg(Document.embedding)).where(Document.id.in_(doc_ids))
    )
    return result.scalar()
```

---

## Performance Optimization

### Query Optimization Checklist

```python
from sqlalchemy import text

async def optimize_query_performance(session: AsyncSession):
    """Apply performance optimizations for vector queries."""

    # 1. Increase work memory for complex queries
    await session.execute(text("SET work_mem = '256MB'"))

    # 2. Configure HNSW for better recall
    await session.execute(text("SET hnsw.ef_search = 100"))

    # 3. Enable iterative scans for filtered queries
    await session.execute(text("SET hnsw.iterative_scan = 'strict_order'"))

    # 4. Disable JIT for simple queries (can reduce overhead)
    await session.execute(text("SET jit = off"))
```

### Storage Optimization

```python
async def optimize_vector_storage(session: AsyncSession):
    """Configure vector column for optimal storage."""
    # Store vectors inline to reduce TOAST overhead
    await session.execute(text(
        "ALTER TABLE documents ALTER COLUMN embedding SET STORAGE PLAIN"
    ))
```

### Index Maintenance

```python
async def maintain_indexes(session: AsyncSession):
    """Regular index maintenance for optimal performance."""
    # Reindex concurrently
    await session.execute(text(
        "REINDEX INDEX CONCURRENTLY documents_embedding_hnsw_idx"
    ))

    # Vacuum to reclaim space
    await session.execute(text("VACUUM ANALYZE documents"))
```

### Query Analysis

```python
async def analyze_query_performance(session: AsyncSession, query_embedding: list):
    """Analyze query execution plan."""
    result = await session.execute(text(
        f"EXPLAIN ANALYZE "
        f"SELECT * FROM documents "
        f"ORDER BY embedding <-> '{query_embedding}' "
        f"LIMIT 5"
    ))

    for row in result:
        print(row[0])
```

### Monitoring

```python
async def get_index_size(session: AsyncSession, index_name: str):
    """Check index size."""
    result = await session.execute(text(
        f"SELECT pg_size_pretty(pg_relation_size('{index_name}'))"
    ))
    return result.scalar()

async def get_slow_queries(session: AsyncSession):
    """Retrieve slowest queries (requires pg_stat_statements)."""
    await session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_stat_statements"))

    result = await session.execute(text(
        "SELECT query, calls, "
        "ROUND((total_plan_time + total_exec_time) / calls) AS avg_time_ms, "
        "ROUND((total_plan_time + total_exec_time) / 60000) AS total_time_min "
        "FROM pg_stat_statements "
        "ORDER BY total_plan_time + total_exec_time DESC "
        "LIMIT 20"
    ))
    return result.all()
```

---

## Connection Pooling

### Production Pool Configuration

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",

    # Pool configuration
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,  # Base number of connections
    max_overflow=5,  # Additional connections under load
    pool_timeout=30,  # Seconds to wait for connection
    pool_recycle=3600,  # Recycle connections after 1 hour

    # Health checks
    pool_pre_ping=True,  # Check connection health before use

    # Execution options
    echo=False,  # Set to True for debugging
    echo_pool=False,  # Log pool checkouts/checkins

    # Connection arguments
    connect_args={
        "server_settings": {
            "jit": "off",  # Disable JIT for simpler queries
            "application_name": "rag_application",
        },
        "command_timeout": 60,  # Query timeout in seconds
    },
)
```

### Connection Pool Monitoring

```python
async def monitor_pool():
    """Monitor connection pool status."""
    pool = engine.pool

    print(f"Pool size: {pool.size()}")
    print(f"Checked out connections: {pool.checkedout()}")
    print(f"Overflow: {pool.overflow()}")
    print(f"Status: {pool.status()}")
```

### Handling Connection Issues

```python
from sqlalchemy.exc import DBAPIError
from sqlalchemy import select

async def resilient_query(session: AsyncSession, query_embedding: list, max_retries: int = 3):
    """Execute query with automatic retry on connection errors."""
    for attempt in range(max_retries):
        try:
            result = await session.execute(
                select(Document)
                .order_by(Document.embedding.l2_distance(query_embedding))
                .limit(5)
            )
            return result.scalars().all()
        except DBAPIError as err:
            if err.connection_invalidated and attempt < max_retries - 1:
                # Connection was invalidated, retry
                await session.rollback()
                continue
            raise
```

### Multiprocessing Considerations

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine

def create_engine_for_worker():
    """Create a new engine after forking to avoid connection sharing."""
    # Dispose parent's engine before fork
    if 'engine' in globals():
        engine.dispose()

    # Create new engine in worker
    return create_async_engine(
        "postgresql+asyncpg://user:password@localhost/dbname",
        pool_pre_ping=True,
    )

# Usage in multiprocessing
def worker_function():
    engine = create_engine_for_worker()
    # Use engine in worker process
```

### Disabling Pooling (for shared engines across event loops)

```python
from sqlalchemy.pool import NullPool

# Use when sharing engine across multiple event loops
engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",
    poolclass=NullPool,  # No connection pooling
)
```

---

## Best Practices

### 1. Embedding Normalization

```python
import numpy as np

def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """
    Normalize embeddings to unit length for cosine similarity.

    When using cosine distance, normalized vectors make L2 distance
    and cosine distance mathematically equivalent, allowing use of
    faster L2 operations.
    """
    norm = np.linalg.norm(embedding)
    if norm > 0:
        return embedding / norm
    return embedding

# With normalized embeddings, these are equivalent:
# - cosine_distance(a, b)
# - l2_distance(normalize(a), normalize(b))
```

### 2. Dimension Reduction for Faster Indexing

```python
from sqlalchemy import func, Index

# For very large datasets, consider storing reduced dimensions for indexing
# and full dimensions for re-ranking

class Document(Base):
    __tablename__ = "documents"

    id = mapped_column(Integer, primary_key=True)
    embedding_full = mapped_column(Vector(768))
    embedding_reduced = mapped_column(Vector(256))  # PCA/UMAP reduced

# Index on reduced dimensions
reduced_index = Index(
    'documents_embedding_reduced_idx',
    Document.embedding_reduced,
    postgresql_using='hnsw',
    postgresql_ops={'embedding_reduced': 'vector_l2_ops'}
)

# Two-stage retrieval
async def two_stage_search(session: AsyncSession, query_embedding: list, limit: int = 5):
    """First stage: fast search on reduced embeddings, second stage: re-rank with full."""
    # Stage 1: Get candidates using reduced embeddings
    candidates = await session.execute(
        select(Document)
        .order_by(Document.embedding_reduced.l2_distance(query_embedding[:256]))
        .limit(limit * 4)  # Over-fetch
    )
    candidate_docs = candidates.scalars().all()

    # Stage 2: Re-rank with full embeddings
    full_query_embedding = query_embedding  # Full 768 dimensions
    reranked = sorted(
        candidate_docs,
        key=lambda doc: np.linalg.norm(np.array(doc.embedding_full) - np.array(full_query_embedding))
    )

    return reranked[:limit]
```

### 3. Database Migrations with Alembic

```python
# alembic/versions/001_add_pgvector.py
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

def upgrade():
    # Enable extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(768), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Create index
    op.execute(
        "CREATE INDEX documents_embedding_hnsw_idx "
        "ON documents USING hnsw (embedding vector_l2_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )

def downgrade():
    op.drop_table('documents')
    op.execute("DROP EXTENSION IF EXISTS vector")
```

### 4. Error Handling

```python
from sqlalchemy.exc import IntegrityError, DBAPIError
import logging

logger = logging.getLogger(__name__)

async def safe_insert_document(
    session: AsyncSession,
    content: str,
    embedding: list[float]
) -> Document | None:
    """Insert document with comprehensive error handling."""
    try:
        # Validate embedding dimension
        if len(embedding) != 768:
            raise ValueError(f"Expected 768 dimensions, got {len(embedding)}")

        doc = Document(content=content, embedding=embedding)
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        return doc

    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Integrity error inserting document: {e}")
        return None

    except DBAPIError as e:
        await session.rollback()
        logger.error(f"Database error: {e}")
        if e.connection_invalidated:
            logger.warning("Connection invalidated, will reconnect on next query")
        return None

    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error: {e}")
        raise
```

### 5. Testing Strategies

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

@pytest.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost/test_db",
        poolclass=NullPool,  # No pooling for tests
        echo=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """Create test session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

@pytest.mark.asyncio
async def test_similarity_search(test_session):
    """Test semantic search functionality."""
    # Insert test documents
    embeddings = np.random.rand(10, 768).tolist()
    for i, emb in enumerate(embeddings):
        doc = Document(content=f"Test document {i}", embedding=emb)
        test_session.add(doc)
    await test_session.commit()

    # Query
    query_embedding = embeddings[0]
    results = await semantic_search(test_session, query_embedding, limit=5)

    assert len(results) == 5
    assert results[0][0].content == "Test document 0"  # Most similar to itself
```

### 6. Configuration Management

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class DatabaseSettings(BaseSettings):
    """Database configuration from environment."""
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str

    pool_size: int = 10
    max_overflow: int = 5
    pool_timeout: int = 30
    pool_pre_ping: bool = True

    embedding_dimension: int = 768
    hnsw_m: int = 16
    hnsw_ef_construction: int = 64
    hnsw_ef_search: int = 100

    class Config:
        env_file = ".env"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

@lru_cache()
def get_settings() -> DatabaseSettings:
    return DatabaseSettings()

# Usage
settings = get_settings()
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_timeout=settings.pool_timeout,
    pool_pre_ping=settings.pool_pre_ping,
)
```

### 7. Performance Benchmarking

```python
import time
import asyncio
from typing import Callable

async def benchmark_query(
    session: AsyncSession,
    query_func: Callable,
    iterations: int = 100
) -> dict:
    """Benchmark a query function."""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        await query_func(session)
        end = time.perf_counter()
        times.append(end - start)

    return {
        "mean": np.mean(times),
        "median": np.median(times),
        "p95": np.percentile(times, 95),
        "p99": np.percentile(times, 99),
        "min": np.min(times),
        "max": np.max(times),
    }

# Usage
async def run_benchmark():
    async with async_session() as session:
        random_embedding = np.random.rand(768).tolist()

        results = await benchmark_query(
            session,
            lambda s: semantic_search(s, random_embedding, limit=5),
            iterations=100
        )

        print(f"Mean query time: {results['mean']*1000:.2f}ms")
        print(f"P95 query time: {results['p95']*1000:.2f}ms")
```

---

## Summary

This guide covers the essential patterns for building production RAG applications with PostgreSQL and pgvector:

1. **Use asyncpg** with SQLAlchemy 2.x for best async performance
2. **Choose HNSW indexes** for production (better recall than IVFFlat)
3. **Normalize embeddings** when using cosine similarity
4. **Configure connection pooling** appropriately for your workload
5. **Enable pool_pre_ping** for connection health checks
6. **Monitor performance** with EXPLAIN ANALYZE and pg_stat_statements
7. **Use filtered searches** with appropriate B-tree indexes on metadata
8. **Implement hybrid search** for better retrieval quality
9. **Test thoroughly** with realistic embedding dimensions and data volumes
10. **Consider two-stage retrieval** for very large datasets

For 768-dimensional embeddings typical of models like `sentence-transformers/all-mpnet-base-v2` or OpenAI's `text-embedding-ada-002`, these patterns provide a solid foundation for scalable RAG applications.
