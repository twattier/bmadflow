# Monitoring

## Overview

BMADFlow implements **structured logging** for application observability in POC scope. Production-grade monitoring services (Datadog, New Relic, Prometheus) are intentionally excluded per PRD requirements (local-only POC, NFR5).

---

## Application Logging

### Backend Logging (Python)

**Configuration:**
```python
# app/config.py
import logging
import sys

def setup_logging():
    """Configure structured JSON logging."""
    log_level = os.getenv("LOG_LEVEL", "INFO")

    logging.basicConfig(
        level=getattr(logging, log_level),
        format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    logger = logging.getLogger("bmadflow")
    return logger
```

**Logging Patterns:**
```python
# app/services/project_doc_service.py
import logging

logger = logging.getLogger(__name__)

async def sync_project_doc(self, project_doc_id: UUID):
    logger.info(f"Sync started: project_doc_id={project_doc_id}")

    try:
        files = await self.github_service.fetch_files(project_doc.github_url)
        logger.info(f"Fetched {len(files)} files from GitHub")

        for file in files:
            await self.process_file(file)

        logger.info(f"Sync completed: project_doc_id={project_doc_id}, file_count={len(files)}")
        return SyncResult(status="success", file_count=len(files))

    except RateLimitExceededError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        raise

    except Exception as e:
        logger.error(f"Sync failed: project_doc_id={project_doc_id}, error={str(e)}", exc_info=True)
        raise
```

**Log Levels:**
- **DEBUG**: Detailed diagnostic info (development only)
- **INFO**: General informational messages (sync started, completed)
- **WARNING**: Potentially problematic situations (rate limit approaching)
- **ERROR**: Error events (sync failed, API error)
- **CRITICAL**: Severe errors (startup validation failed)

**View Logs (Docker):**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Filter by level (JSON logs)
docker-compose logs backend | jq 'select(.level == "ERROR")'
```

### Frontend Logging (Browser Console)

**Configuration:**
```tsx
// src/utils/logger.ts
const isDev = import.meta.env.DEV;

export const logger = {
  debug: (...args: any[]) => {
    if (isDev) console.log('[DEBUG]', new Date().toISOString(), ...args);
  },
  info: (...args: any[]) => {
    if (isDev) console.info('[INFO]', new Date().toISOString(), ...args);
  },
  warn: (...args: any[]) => {
    console.warn('[WARN]', new Date().toISOString(), ...args);
  },
  error: (...args: any[]) => {
    console.error('[ERROR]', new Date().toISOString(), ...args);
  },
};
```

**Usage:**
```tsx
// src/api/hooks/useProjects.ts
import { logger } from '@/utils/logger';

export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      logger.debug('Fetching projects...');
      const { data } = await apiClient.get<Project[]>('/projects');
      logger.info('Projects loaded:', data.length);
      return data;
    },
    onError: (error) => {
      logger.error('Failed to fetch projects:', error);
    },
  });
}
```

**View Logs:**
- Browser DevTools → Console tab
- Filter by level (Info, Warn, Error)

---

## Request Logging

### Backend Request Logging

**FastAPI Middleware:**
```python
# app/main.py
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response
    duration = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"status={response.status_code} duration={duration:.3f}s"
    )

    return response
```

**Example Logs:**
```json
{"timestamp": "2025-10-06T10:15:23", "level": "INFO", "message": "Request: GET /api/projects"}
{"timestamp": "2025-10-06T10:15:23", "level": "INFO", "message": "Response: GET /api/projects status=200 duration=0.045s"}
```

### Frontend Request Logging (Axios Interceptor)

```tsx
// src/api/client.ts
import { logger } from '@/utils/logger';

apiClient.interceptors.request.use(
  (config) => {
    logger.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  }
);

apiClient.interceptors.response.use(
  (response) => {
    logger.debug(
      `API Response: ${response.config.method?.toUpperCase()} ${response.config.url} status=${response.status}`
    );
    return response;
  },
  (error) => {
    logger.error(
      `API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} status=${error.response?.status}`
    );
    return Promise.reject(error);
  }
);
```

---

## Health Checks

### Backend Health Endpoint

```python
# app/api/v1/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint with dependency status."""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health["services"]["database"] = "healthy"
    except Exception as e:
        health["services"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "unhealthy"

    # Check Ollama
    try:
        await ollama.list()
        health["services"]["ollama"] = "healthy"
    except Exception as e:
        health["services"]["ollama"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"  # Non-critical

    return health
```

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-06T10:15:23Z",
  "services": {
    "database": "healthy",
    "ollama": "healthy"
  }
}
```

**Use Health Check:**
```bash
# Manual check
curl http://localhost:8000/api/health | jq

# Docker health check (in docker-compose.yml)
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## Metrics (POC Scope)

### Simple Metrics via Dashboard

**Backend Endpoint:**
```python
# app/api/v1/dashboard.py
@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """Get application metrics."""
    return {
        "total_projects": await project_repo.count(),
        "total_documents": await document_repo.count(),
        "total_chunks": await chunk_repo.count(),
        "total_conversations": await conversation_repo.count(),
    }
```

**Frontend Display:**
```tsx
// src/pages/Dashboard.tsx
function Dashboard() {
  const { data: metrics } = useDashboardMetrics();

  return (
    <div className="grid grid-cols-4 gap-4">
      <MetricCard title="Projects" value={metrics?.total_projects} />
      <MetricCard title="Documents" value={metrics?.total_documents} />
      <MetricCard title="Chunks" value={metrics?.total_chunks} />
      <MetricCard title="Conversations" value={metrics?.total_conversations} />
    </div>
  );
}
```

---

## Error Tracking

### Backend Error Logging

**Structured Error Logs:**
```python
try:
    result = await some_operation()
except Exception as e:
    logger.error(
        f"Operation failed: {str(e)}",
        extra={
            "error_type": type(e).__name__,
            "project_doc_id": str(project_doc_id),
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )
    raise
```

**View Error Logs:**
```bash
# Filter for ERROR level
docker-compose logs backend | grep ERROR

# With jq (JSON logs)
docker-compose logs backend | jq 'select(.level == "ERROR")'
```

### Frontend Error Logging

**Global Error Handler:**
```tsx
// src/App.tsx
window.addEventListener('error', (event) => {
  logger.error('Uncaught error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  logger.error('Unhandled promise rejection:', event.reason);
});
```

---

## Alerting Thresholds

### POC Alerting Strategy

For POC deployment, alerting is **log-based** (developers monitor logs manually). The thresholds below define when issues should be investigated or escalated.

**Alert Severity Levels:**
- 🔴 **CRITICAL**: Immediate action required - service unusable
- 🟠 **WARNING**: Degraded performance - investigate soon
- 🟡 **INFO**: Notable event - monitor for patterns

---

### Performance Thresholds

| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| **Vector Search Latency** | >500ms | 🟠 WARNING | Check pgvector index health, query filter scope |
| **Vector Search Latency** | >1000ms | 🔴 CRITICAL | Index rebuild may be needed, investigate query plan |
| **RAG Query (Cloud LLM)** | >3s | 🟠 WARNING | Check LLM API response times, network latency |
| **RAG Query (Cloud LLM)** | >5s | 🔴 CRITICAL | Consider LLM provider fallback, check API quotas |
| **RAG Query (Ollama)** | >10s | 🟠 WARNING | Expected for local inference, acceptable |
| **RAG Query (Ollama)** | >20s | 🔴 CRITICAL | Check Ollama service health, GPU availability |
| **Markdown Rendering** | >1s | 🟠 WARNING | Check document size, optimize rendering |
| **File Tree Load** | >2s | 🟠 WARNING | Check file count, consider pagination |
| **Sync Duration** | >5min | 🟠 WARNING | Expected for large repos, monitor for timeout |
| **Sync Duration** | >10min | 🔴 CRITICAL | Investigate GitHub rate limits, network issues |

**Log Detection:**
```bash
# Alert if vector search exceeds 1s
docker-compose logs backend | grep "vector_search" | jq 'select(.duration > 1.0)'

# Alert if sync takes >10min
docker-compose logs backend | grep "Sync completed" | jq 'select(.duration > 600)'
```

---

### Error Rate Thresholds

| Error Type | Threshold | Severity | Action |
|-----------|-----------|----------|--------|
| **Sync Failures** | 3 consecutive failures | 🔴 CRITICAL | Check GitHub API limits, network connectivity |
| **Database Errors** | Any | 🔴 CRITICAL | Check PostgreSQL health, connection pool |
| **Ollama Connection Errors** | 3 in 5 minutes | 🔴 CRITICAL | Ensure Ollama running: `ollama list` |
| **LLM Provider Errors** | 5 in 5 minutes | 🟠 WARNING | Check API quotas, try fallback provider |
| **API 5xx Errors** | >5% of requests | 🔴 CRITICAL | Check backend logs for stack traces |
| **API 4xx Errors** | >20% of requests | 🟠 WARNING | Investigate client validation issues |
| **Frontend Uncaught Errors** | Any | 🟠 WARNING | Check browser console, React error boundary |

**Log Detection:**
```bash
# Alert on sync failures
docker-compose logs backend | grep "Sync failed" | tail -3

# Alert on database errors
docker-compose logs backend | jq 'select(.level == "ERROR" and .message | contains("database"))'

# Alert on high 5xx rate (>5%)
docker-compose logs backend | grep "Response:" | awk '{print $NF}' | grep "status=5" | wc -l
```

---

### Resource Utilization Thresholds

| Resource | Threshold | Severity | Action |
|----------|-----------|----------|--------|
| **PostgreSQL Connections** | >80% of pool_size | 🟠 WARNING | Increase pool_size in settings, investigate leaks |
| **Database Disk Usage** | >80% | 🟠 WARNING | Check vector storage growth, consider cleanup |
| **Database Disk Usage** | >90% | 🔴 CRITICAL | Immediate cleanup or disk expansion needed |
| **Memory (Backend)** | >2GB | 🟠 WARNING | Check for memory leaks, optimize embedding batching |
| **Embedding Queue** | >100 pending chunks | 🟠 WARNING | Ollama may be slow, consider batch size tuning |

**Detection Commands:**
```bash
# Check PostgreSQL connections
docker exec bmadflow-db psql -U bmadflow -c "SELECT count(*) FROM pg_stat_activity;"

# Check database size
docker exec bmadflow-db psql -U bmadflow -c "SELECT pg_size_pretty(pg_database_size('bmadflow'));"

# Check Docker container memory
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"
```

---

### Service Health Thresholds

| Service | Threshold | Severity | Action |
|---------|-----------|----------|--------|
| **Backend Health Check** | Fails 3 consecutive times | 🔴 CRITICAL | Restart backend: `docker-compose restart backend` |
| **Database Health Check** | Fails 2 consecutive times | 🔴 CRITICAL | Restart PostgreSQL: `docker-compose restart db` |
| **Ollama Availability** | Unreachable for >1 minute | 🔴 CRITICAL | Start Ollama: `ollama serve`, check model: `ollama list` |
| **GitHub API Rate Limit** | <10 requests remaining | 🟠 WARNING | Wait for reset or add GITHUB_TOKEN for 5000 req/hr |
| **GitHub API Rate Limit** | 0 requests remaining | 🔴 CRITICAL | Sync blocked, wait for reset time (header: X-RateLimit-Reset) |

**Health Check Command:**
```bash
# Check all services health
curl -s http://localhost:8000/api/health | jq

# Monitor health check continuously
watch -n 30 'curl -s http://localhost:8000/api/health | jq'
```

---

### Data Quality Thresholds

| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| **Empty Embeddings** | >5% of chunks | 🟠 WARNING | Check Ollama connectivity during sync |
| **Missing Header Anchors** | >30% of chunks | 🟡 INFO | Expected for non-markdown files, acceptable |
| **Vector Dimension Mismatch** | Any | 🔴 CRITICAL | Embedding model changed, database rebuild required |
| **Sync Success Rate** | <90% | 🟠 WARNING | Investigate GitHub API errors, network issues |

**Data Quality Queries:**
```sql
-- Check for empty embeddings
SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM chunks) as empty_embedding_pct
FROM chunks WHERE embedding IS NULL;

-- Check header anchor coverage
SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM chunks) as anchor_coverage_pct
FROM chunks WHERE header_anchor IS NOT NULL;
```

---

### Implementing Alerting (Production)

**For production deployment, implement automated alerting:**

1. **Log-Based Alerts (ELK + ElastAlert):**
   ```yaml
   # elastalert/rules/vector_search_slow.yaml
   name: Vector Search Slow
   type: metric_aggregation
   index: bmadflow-logs-*
   metric_agg_key: duration
   metric_agg_type: avg
   threshold: 1.0  # 1 second
   alert: email
   email: ops-team@example.com
   ```

2. **Prometheus + Grafana Alerts:**
   ```yaml
   # prometheus/alerts.yml
   groups:
   - name: bmadflow
     rules:
     - alert: HighVectorSearchLatency
       expr: vector_search_duration_seconds > 1.0
       for: 5m
       annotations:
         summary: "Vector search exceeding 1s threshold"
   ```

3. **Application-Level Alerts (Sentry):**
   ```python
   import sentry_sdk

   # Alert on specific error types
   if sync_failures >= 3:
       sentry_sdk.capture_message("Sync failing repeatedly", level="error")
   ```

---

## Production Monitoring (Out of Scope for POC)

**Future Enhancements:**

### APM (Application Performance Monitoring)
- **Tools**: Datadog, New Relic, Prometheus + Grafana
- **Metrics**: Request latency, throughput, error rates
- **Traces**: Distributed tracing for RAG pipeline

### Log Aggregation
- **Tools**: ELK Stack (Elasticsearch, Logstash, Kibana), Splunk
- **Features**: Centralized log search, dashboards, alerts

### Error Tracking
- **Tools**: Sentry, Rollbar
- **Features**: Error grouping, stack traces, release tracking, user context

### Uptime Monitoring
- **Tools**: Pingdom, UptimeRobot
- **Features**: Endpoint monitoring, alerting, status pages

### Alerting Systems
- **Tools**: PagerDuty, Opsgenie
- **Integration**: Trigger alerts based on thresholds defined above
- **Escalation**: Auto-escalate critical alerts after timeout

---

## Log Retention (POC)

**Docker Logs:**
- Retained in container until `docker-compose down`
- No automatic rotation (acceptable for POC)

**Production Retention:**
- 30-90 days for application logs
- 1 year for audit logs
- Use log rotation (logrotate) or cloud log services

---

## Troubleshooting with Logs

### Common Scenarios

**Backend Won't Start:**
```bash
docker-compose logs backend | grep ERROR
# Look for: Database connection failed, Ollama validation failed
```

**Sync Operation Failing:**
```bash
docker-compose logs backend | grep "sync_project_doc"
# Look for: GitHub rate limit, Ollama connection error, file processing errors
```

**Frontend API Errors:**
```
Browser DevTools → Console → Filter: Error
Network → Failed requests → Check status code, response body
```

---

## Related Documentation

- **Error Handling**: [error-handling.md](error-handling.md)
- **Deployment**: [deployment.md](deployment.md)
- **Development Workflow**: [development-workflow.md](development-workflow.md)

---
