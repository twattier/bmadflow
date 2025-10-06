# Security & Performance

## Security

### POC Security Posture

⚠️ **IMPORTANT**: This is a **POC for local-only deployment**. The following security measures are intentionally simplified or omitted:

**Acceptable for POC (NOT Production):**
- No API authentication (single-tenant, localhost-only)
- No pgAdmin authentication
- Simple database passwords in `.env`
- HTTP-only (no HTTPS/TLS)
- No secrets management (API keys in `.env`)
- No network isolation (all services on localhost)

**Security Measures Implemented:**

#### 1. Input Validation (Pydantic)

All API inputs validated via Pydantic schemas:
```python
class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
```

#### 2. SQL Injection Prevention

Use SQLAlchemy ORM (parameterized queries):
```python
# Good: Parameterized query
project = await session.execute(
    select(Project).where(Project.id == project_id)
)

# Bad: SQL injection risk
query = f"SELECT * FROM projects WHERE id = '{project_id}'"  # ❌ Never do this
```

#### 3. CORS Configuration

Restrict frontend origin:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Only frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. Dependency Security

Regularly update dependencies:
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
npm audit fix
```

#### 5. Secrets Management

API keys in `.env` (gitignored):
```bash
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
```

**Production Requirements (Out of Scope):**
- JWT or OAuth2 authentication
- Role-based access control (RBAC)
- HTTPS/TLS certificates
- Secrets management (Vault, AWS Secrets Manager)
- Database connection encryption
- API rate limiting per user
- Security headers (HSTS, CSP, X-Frame-Options)
- Vulnerability scanning (Snyk, Dependabot)

---

## Performance

### Performance Targets (from PRD)

| Operation | Target | Strategy |
|-----------|--------|----------|
| Documentation Sync | <5min per ProjectDoc | Batch processing, async operations |
| RAG Query (Cloud LLM) | <3s | Optimized vector search, connection pooling |
| RAG Query (Ollama) | <10s | Acceptable for local inference |
| Vector Similarity Search | <500ms | HNSW index, project-scoped queries |
| Markdown Rendering | <1s | Virtual scrolling, lazy loading |
| Explorer Page Load | <2s | Code splitting, cached API responses |

### Backend Performance Optimization

#### 1. Database Query Optimization

**Use Indexes:**
```sql
-- HNSW index for vector search
CREATE INDEX chunks_embedding_idx ON chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Composite index for filtered queries
CREATE INDEX conversations_project_updated_idx
ON conversations(project_id, updated_at DESC);
```

**Eager Loading (Avoid N+1):**
```python
# Good: Single query with join
projects = await session.execute(
    select(Project).options(joinedload(Project.project_docs))
)

# Bad: N+1 queries
projects = await session.execute(select(Project))
for project in projects:
    docs = await session.execute(
        select(ProjectDoc).where(ProjectDoc.project_id == project.id)
    )  # ❌ Separate query per project
```

#### 2. Connection Pooling

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,          # Concurrent connections
    max_overflow=20,       # Extra connections when pool full
    pool_pre_ping=True,    # Verify connection before use
    pool_recycle=3600,     # Recycle connections after 1 hour
)
```

#### 3. Async Operations

Use async for I/O-bound operations:
```python
# Parallel embedding generation
embeddings = await asyncio.gather(*[
    generate_embedding(chunk.text)
    for chunk in chunks
])
```

#### 4. Caching (Future Enhancement)

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_llm_provider_config(provider_id: UUID) -> dict:
    """Cache LLM provider configs."""
    return llm_provider_repo.get_config(provider_id)
```

### Frontend Performance Optimization

#### 1. Code Splitting

```tsx
// Lazy load routes
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Chat = lazy(() => import('./pages/Chat'));

// Wrap in Suspense
<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/chat" element={<Chat />} />
  </Routes>
</Suspense>
```

#### 2. Virtual Scrolling

```tsx
// react-arborist for file tree (1000+ files)
<Tree
  data={fileTree}
  height={800}
  width="100%"
  virtualizeOptions={{ overscan: 10 }}
>
  {/* Tree nodes */}
</Tree>
```

#### 3. Memoization

```tsx
// Expensive computation
const flattenedTree = useMemo(() => {
  return flattenFileTree(fileTree);
}, [fileTree]);

// Stable callbacks
const handleSelect = useCallback((node: FileNode) => {
  setSelectedNode(node);
}, []);
```

#### 4. React Query Caching

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,   // 5 minutes
      cacheTime: 1000 * 60 * 30,  // 30 minutes
      refetchOnWindowFocus: false,
    },
  },
});
```

#### 5. Image/Asset Optimization

```tsx
// Lazy load images
<img src={imageUrl} loading="lazy" alt="..." />

// Optimize bundle size
import { Button } from '@/components/ui/button'; // Tree-shakeable imports
```

### Database Performance

#### 1. pgvector Optimization

**HNSW Index Configuration:**
```sql
-- Tuned for POC (768-dim embeddings, ~100K chunks)
CREATE INDEX chunks_embedding_idx ON chunks
USING hnsw (embedding vector_cosine_ops)
WITH (
  m = 16,              -- Connections per node (higher = better recall, slower build)
  ef_construction = 64 -- Build-time quality (higher = better quality, slower build)
);
```

**Query Optimization:**
```python
# Limit search space with filters
query = select(Chunk).where(
    Chunk.project_id == project_id,  # Filter by project first
    Chunk.embedding.cosine_distance(query_embedding) < 0.3  # Similarity threshold
).order_by(
    Chunk.embedding.cosine_distance(query_embedding)
).limit(5)
```

#### 2. Connection Pooling

**PostgreSQL max_connections**: Ensure sufficient connections for concurrent users

**SQLAlchemy pool_size**: Match expected concurrent requests (10-20 for POC)

### Ollama Performance

**Batch Embedding Generation:**
```python
# Process chunks in batches
async def generate_embeddings_batch(texts: List[str], batch_size: int = 10):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = await asyncio.gather(*[
            generate_embedding(text) for text in batch
        ])
        embeddings.extend(batch_embeddings)
    return embeddings
```

**Model Optimization:**
- Use GPU acceleration if available (Ollama auto-detects)
- Consider smaller model for faster inference (nomic-embed-text is optimal for POC)

---

## Monitoring & Profiling

### Backend Profiling

**cProfile:**
```bash
python -m cProfile -o profile.stats -m uvicorn app.main:app

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats
```

**Slow Query Logging (PostgreSQL):**
```sql
-- Enable slow query log
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries >1s
SELECT pg_reload_conf();
```

### Frontend Profiling

**React DevTools Profiler:**
1. Install React DevTools browser extension
2. Open DevTools → Profiler tab
3. Record interaction
4. Analyze render times

**Lighthouse:**
```bash
# Run Lighthouse audit
npm install -g lighthouse
lighthouse http://localhost:3000 --view
```

**Bundle Size Analysis:**
```bash
# Vite build with analysis
npm run build
npx vite-bundle-visualizer
```

---

## Load Testing (Future)

**Backend Load Testing (Locust):**
```python
from locust import HttpUser, task

class BMADFlowUser(HttpUser):
    @task
    def get_projects(self):
        self.client.get("/api/projects")

    @task
    def vector_search(self):
        self.client.post("/api/projects/123/search", json={"query": "test"})
```

**Run Load Test:**
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## Related Documentation

- **Backend Architecture**: [backend-architecture.md](backend-architecture.md)
- **Frontend Architecture**: [frontend-architecture.md](frontend-architecture.md)
- **Database Schema**: [database-schema.md](database-schema.md)
- **Error Handling**: [error-handling.md](error-handling.md)

---
