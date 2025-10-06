# Error Handling

## Overview

BMADFlow implements **defensive error handling** across all layers (API, service, repository) with consistent error responses, retry logic for transient failures, and user-friendly error messages. This document defines error handling patterns, HTTP status codes, and recovery strategies.

---

## HTTP Status Codes

### Standard Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 OK | Success (GET, PUT, DELETE) | Resource retrieved/updated/deleted |
| 201 Created | Resource created | POST successful |
| 202 Accepted | Async operation started | Sync operation triggered |
| 400 Bad Request | Client error (validation) | Invalid request payload |
| 404 Not Found | Resource doesn't exist | Project ID not found |
| 409 Conflict | Resource conflict | Duplicate project name |
| 422 Unprocessable Entity | Semantic error | Invalid GitHub URL format |
| 429 Too Many Requests | Rate limit exceeded | GitHub API rate limit |
| 500 Internal Server Error | Server error | Unexpected exception |
| 503 Service Unavailable | Dependency unavailable | Ollama service down |

---

## Backend Error Handling

### API Layer (Routes)

**FastAPI Exception Handling:**
```python
from fastapi import HTTPException, status

@router.get("/projects/{project_id}")
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service)
):
    try:
        project = await service.get_project(project_id)
        return project
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

**Global Exception Handler:**
```python
# app/main.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )
```

### Service Layer

**Custom Exceptions:**
```python
# app/exceptions.py
class BMADFlowError(Exception):
    """Base exception for BMADFlow"""
    pass

class ProjectNotFoundError(BMADFlowError):
    """Project not found"""
    pass

class GitHubAPIError(BMADFlowError):
    """GitHub API error"""
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class RateLimitExceededError(GitHubAPIError):
    """GitHub rate limit exceeded"""
    def __init__(self, reset_time: int):
        self.reset_time = reset_time
        super().__init__(f"Rate limit exceeded. Resets at {reset_time}", 429)

class OllamaConnectionError(BMADFlowError):
    """Ollama service unavailable"""
    pass
```

**Service Error Handling:**
```python
# app/services/project_doc_service.py
class ProjectDocService:
    async def sync_project_doc(self, project_doc_id: UUID) -> SyncResult:
        try:
            # Fetch GitHub files
            files = await self.github_service.fetch_files(project_doc.github_url)

            # Process and embed
            for file in files:
                await self.document_service.process_file(file)

            # Update sync timestamp
            await self.project_doc_repo.update_sync_timestamp(project_doc_id)

            return SyncResult(status="success", file_count=len(files))

        except RateLimitExceededError as e:
            logger.warning(f"GitHub rate limit exceeded: {e}")
            raise  # Re-raise for API layer to handle

        except OllamaConnectionError as e:
            logger.error(f"Ollama unavailable during sync: {e}")
            raise HTTPException(
                status_code=503,
                detail="Embedding service unavailable. Check Ollama is running."
            )

        except Exception as e:
            logger.error(f"Sync failed for {project_doc_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Sync failed: {str(e)}"
            )
```

### Retry Logic

**Decorator for Transient Failures:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class EmbeddingService:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding with retry on network errors."""
        try:
            response = await ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
            return response["embedding"]
        except httpx.RequestError as e:
            logger.warning(f"Ollama request failed, retrying: {e}")
            raise  # Tenacity will retry
```

**GitHub Rate Limit Handling:**
```python
class GitHubService:
    async def fetch_with_rate_limit_handling(self, url: str) -> dict:
        """Fetch GitHub API with rate limit awareness."""
        response = await self.client.get(url)

        # Check rate limit headers
        remaining = int(response.headers.get("X-RateLimit-Remaining", 999))
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))

        if response.status_code == 403 and remaining == 0:
            # Rate limit exceeded
            wait_seconds = reset_time - time.time()
            raise RateLimitExceededError(reset_time)

        if remaining < 5:
            # Approaching limit, log warning
            logger.warning(f"GitHub rate limit low: {remaining} remaining")

        response.raise_for_status()
        return response.json()
```

### Repository Layer

**Database Error Handling:**
```python
from sqlalchemy.exc import IntegrityError, OperationalError

class ProjectRepository:
    async def create(self, name: str, description: str) -> Project:
        try:
            project = Project(name=name, description=description)
            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)
            return project

        except IntegrityError as e:
            await self.db.rollback()
            if "unique constraint" in str(e).lower():
                raise HTTPException(
                    status_code=409,
                    detail=f"Project with name '{name}' already exists"
                )
            raise

        except OperationalError as e:
            await self.db.rollback()
            logger.error(f"Database error creating project: {e}")
            raise HTTPException(
                status_code=503,
                detail="Database unavailable"
            )
```

---

## Frontend Error Handling

### API Error Handling (Axios Interceptor)

```tsx
// src/api/client.ts
import axios from 'axios';
import { toast } from '@/components/ui/use-toast';

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Extract error details
    const status = error.response?.status;
    const detail = error.response?.data?.detail || 'An error occurred';

    // Handle specific status codes
    if (status === 404) {
      toast({
        title: 'Not Found',
        description: detail,
        variant: 'destructive',
      });
    } else if (status === 429) {
      toast({
        title: 'Rate Limit Exceeded',
        description: detail,
        variant: 'destructive',
      });
    } else if (status === 503) {
      toast({
        title: 'Service Unavailable',
        description: detail,
        variant: 'destructive',
      });
    } else if (status >= 500) {
      toast({
        title: 'Server Error',
        description: 'Something went wrong. Please try again.',
        variant: 'destructive',
      });
    }

    return Promise.reject(error);
  }
);
```

### Component Error Boundaries

```tsx
// src/components/common/ErrorBoundary.tsx
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 text-center">
          <h2 className="text-2xl font-bold text-destructive mb-4">
            Something went wrong
          </h2>
          <p className="text-muted-foreground mb-4">
            {this.state.error?.message}
          </p>
          <Button onClick={() => window.location.reload()}>
            Reload Page
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### React Query Error Handling

```tsx
// src/api/hooks/useProjects.ts
export function useProjects() {
  return useQuery<Project[], Error>({
    queryKey: ['projects'],
    queryFn: async () => {
      const { data } = await apiClient.get<Project[]>('/projects');
      return data;
    },
    onError: (error) => {
      console.error('Failed to fetch projects:', error);
      toast({
        title: 'Failed to load projects',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

// Usage in component
function ProjectList() {
  const { data, isLoading, error } = useProjects();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} retry={() => window.location.reload()} />;

  return <div>{/* Render projects */}</div>;
}
```

### User-Friendly Error Messages

**Error Display Component:**
```tsx
// src/components/common/ErrorDisplay.tsx
interface ErrorDisplayProps {
  error: Error;
  retry?: () => void;
}

export function ErrorDisplay({ error, retry }: ErrorDisplayProps) {
  return (
    <Card className="border-destructive">
      <CardHeader>
        <CardTitle className="text-destructive flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          Error
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4">{error.message}</p>
        {retry && (
          <Button onClick={retry} variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Retry
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## Error Logging

### Backend Logging

**Structured Logging:**
```python
import logging
import json

# Configure structured JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
    format="%(message)s"
)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("bmadflow")
logger.addHandler(handler)

# Usage
logger.info("Sync started", extra={"project_doc_id": str(project_doc_id)})
logger.error("Sync failed", extra={"project_doc_id": str(project_doc_id), "error": str(e)})
```

### Frontend Logging

**Console Logging (Development Only):**
```tsx
// src/utils/logger.ts
const isDev = import.meta.env.DEV;

export const logger = {
  debug: (...args: any[]) => {
    if (isDev) console.log('[DEBUG]', ...args);
  },
  info: (...args: any[]) => {
    if (isDev) console.info('[INFO]', ...args);
  },
  warn: (...args: any[]) => {
    console.warn('[WARN]', ...args);
  },
  error: (...args: any[]) => {
    console.error('[ERROR]', ...args);
  },
};

// Usage
logger.info('Project loaded:', project.id);
logger.error('Failed to fetch projects:', error);
```

---

## Common Error Scenarios

### Ollama Not Running

**Symptom**: Backend fails to start or embedding generation fails

**Error Handling:**
```python
# Startup validation
@app.on_event("startup")
async def validate_ollama():
    try:
        await embedding_service.validate_ollama_setup()
    except OllamaConnectionError:
        logger.error("Ollama not available. Start Ollama and run: ollama pull nomic-embed-text")
        # Continue startup (allow app to run, show error in UI)
```

**User Message**: "Embedding service unavailable. Check Ollama is running at localhost:11434"

### GitHub Rate Limit Exceeded

**Symptom**: Sync fails with 403 status

**Error Handling:**
```python
if rate_limit_exceeded:
    reset_time = datetime.fromtimestamp(reset_timestamp)
    raise RateLimitExceededError(
        f"GitHub rate limit exceeded. Resets at {reset_time.strftime('%H:%M:%S')}"
    )
```

**User Message**: "GitHub rate limit exceeded. Resets at 14:35:12. Try again later or add GITHUB_TOKEN to .env for higher limits."

### Database Connection Lost

**Symptom**: SQL queries fail with connection errors

**Error Handling:**
```python
# SQLAlchemy connection pool handles reconnection automatically
# Log error, return 503 to client
raise HTTPException(status_code=503, detail="Database temporarily unavailable")
```

**User Message**: "Database temporarily unavailable. Please try again."

### Malformed Markdown or Mermaid

**Symptom**: Rendering fails with syntax errors

**Error Handling (Frontend):**
```tsx
try {
  mermaid.render('diagram-id', mermaidCode);
} catch (error) {
  console.error('Mermaid rendering failed:', error);
  return (
    <div className="border border-destructive p-4 rounded">
      <p className="text-sm text-destructive">Invalid Mermaid syntax</p>
      <pre className="text-xs mt-2 text-muted-foreground">{mermaidCode}</pre>
    </div>
  );
}
```

**User Message**: "Invalid Mermaid syntax" (shows original code block)

---

## Related Documentation

- **Backend Architecture**: [backend-architecture.md](backend-architecture.md)
- **Frontend Architecture**: [frontend-architecture.md](frontend-architecture.md)
- **Monitoring**: [monitoring.md](monitoring.md)

---
