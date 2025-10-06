# Deployment

## Overview

BMADFlow supports **local-only deployment** on developer workstations using Docker Compose orchestration. Two deployment modes are supported: **Full Docker** (all services containerized) and **Hybrid** (frontend/backend local, database dockerized). This POC explicitly excludes cloud hosting, CI/CD pipelines, and production infrastructure per PRD requirements (NFR5).

**Deployment Modes:**
1. **Full Docker**: All services (frontend, backend, PostgreSQL, pgAdmin) run in Docker containers
2. **Hybrid**: Frontend and backend run locally (hot reload), PostgreSQL and pgAdmin in Docker

**Prerequisites:**
- Docker Desktop installed and running
- Python 3.11+ (Hybrid mode only)
- Node.js 18+ (Hybrid mode only)
- Ollama service running locally with `nomic-embed-text` model

---

## Full Docker Deployment

### Architecture

```mermaid
graph TB
    subgraph "Docker Compose Network"
        FE[Frontend Container<br/>Vite Dev Server<br/>:3000]
        BE[Backend Container<br/>FastAPI + uvicorn<br/>:8000]
        DB[(PostgreSQL + pgvector<br/>:5432)]
        PGA[pgAdmin<br/>:5050]
    end

    OLLAMA[Ollama Service<br/>Host Machine<br/>:11434]

    USER([Developer]) -->|Browser| FE
    FE -->|REST API| BE
    BE -->|SQL Queries| DB
    BE -->|Embeddings| OLLAMA
    USER -.->|DB Admin| PGA
    PGA -.-> DB

    classDef container fill:#0969da,stroke:#0969da,color:#fff
    classDef external fill:#6c757d,stroke:#6c757d,color:#fff

    class FE,BE,PGA,DB container
    class OLLAMA external
```

### Docker Compose Configuration

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL with pgvector
  db:
    image: ankane/pgvector:latest
    container_name: bmadflow-db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-bmadflow}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
      POSTGRES_DB: ${POSTGRES_DB:-bmadflow}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-bmadflow}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - bmadflow-network

  # Backend (FastAPI)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: bmadflow-backend
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-bmadflow}:${POSTGRES_PASSWORD:-changeme}@db:5432/${POSTGRES_DB:-bmadflow}
      OLLAMA_ENDPOINT_URL: ${OLLAMA_ENDPOINT_URL:-http://host.docker.internal:11434}
      BACKEND_PORT: ${BACKEND_PORT:-8000}
      CORS_ORIGINS: http://localhost:${FRONTEND_PORT:-3000}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      OPENAI_API_KEY: ${OPENAI_API_KEY:-}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY:-}
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    volumes:
      - ./backend:/app  # Hot reload support
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    networks:
      - bmadflow-network

  # Frontend (React + Vite)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: bmadflow-frontend
    environment:
      VITE_BACKEND_URL: http://localhost:${BACKEND_PORT:-8000}
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    volumes:
      - ./frontend:/app  # Hot reload support
      - /app/node_modules  # Avoid overwriting node_modules
    depends_on:
      - backend
    command: npm run dev -- --host 0.0.0.0 --port 3000
    networks:
      - bmadflow-network

  # pgAdmin (Database Admin UI)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: bmadflow-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@bmadflow.local
      PGADMIN_DEFAULT_PASSWORD: admin
      PGADMIN_CONFIG_SERVER_MODE: 'False'  # No auth for POC
      PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED: 'False'
    ports:
      - "${PGADMIN_PORT:-5050}:80"
    depends_on:
      - db
    networks:
      - bmadflow-network

volumes:
  postgres_data:

networks:
  bmadflow-network:
    driver: bridge
```

### Backend Dockerfile

**File**: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose.yml)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

**File**: `frontend/Dockerfile`

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Default command (can be overridden in docker-compose.yml)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### Environment Variables

**File**: `.env` (create from `.env.example`)

```bash
# Database Configuration
POSTGRES_USER=bmadflow
POSTGRES_PASSWORD=changeme_in_production
POSTGRES_DB=bmadflow
DATABASE_URL=postgresql+asyncpg://bmadflow:changeme_in_production@localhost:5432/bmadflow

# Port Configuration (adjust if conflicts exist)
FRONTEND_PORT=3000
BACKEND_PORT=8000
POSTGRES_PORT=5432
PGADMIN_PORT=5050

# Ollama Configuration
OLLAMA_ENDPOINT_URL=http://host.docker.internal:11434
EMBEDDING_MODEL=nomic-embed-text

# LLM Provider API Keys (Optional)
OPENAI_API_KEY=
GOOGLE_API_KEY=
LITELLM_CONFIG=

# GitHub API (Optional - increases rate limit from 60 to 5000 req/hr)
GITHUB_TOKEN=

# Application Configuration
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### Deployment Steps

**1. Prerequisites Check**
```bash
# Verify Docker is running
docker --version
docker-compose --version

# Verify Ollama is running with nomic-embed-text model
curl http://localhost:11434/api/tags | grep nomic-embed-text

# If model not installed:
ollama pull nomic-embed-text
```

**2. Configure Environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration (ports, API keys, etc.)
nano .env
```

**3. Start Services**
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

**4. Verify Services**
```bash
# Check service status
docker-compose ps

# Expected output:
# NAME                STATUS    PORTS
# bmadflow-db         Up        0.0.0.0:5432->5432/tcp
# bmadflow-backend    Up        0.0.0.0:8000->8000/tcp
# bmadflow-frontend   Up        0.0.0.0:3000->3000/tcp
# bmadflow-pgadmin    Up        0.0.0.0:5050->80/tcp

# Test backend health
curl http://localhost:8000/api/health

# Access frontend
open http://localhost:3000

# Access pgAdmin
open http://localhost:5050
```

**5. View Logs**
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

**6. Stop Services**
```bash
# Stop all services (preserves data)
docker-compose down

# Stop and remove volumes (deletes database data)
docker-compose down -v
```

---

## Hybrid Deployment

### Architecture

```mermaid
graph TB
    subgraph "Host Machine"
        FE[Frontend Process<br/>npm run dev<br/>:3000]
        BE[Backend Process<br/>uvicorn --reload<br/>:8000]
    end

    subgraph "Docker Compose"
        DB[(PostgreSQL + pgvector<br/>:5432)]
        PGA[pgAdmin<br/>:5050]
    end

    OLLAMA[Ollama Service<br/>localhost:11434]

    USER([Developer]) -->|Browser| FE
    FE -->|REST API| BE
    BE -->|SQL Queries| DB
    BE -->|Embeddings| OLLAMA
    USER -.->|DB Admin| PGA
    PGA -.-> DB

    classDef local fill:#1a7f37,stroke:#1a7f37,color:#fff
    classDef container fill:#0969da,stroke:#0969da,color:#fff
    classDef external fill:#6c757d,stroke:#6c757d,color:#fff

    class FE,BE local
    class DB,PGA container
    class OLLAMA external
```

### Docker Compose Configuration (Hybrid)

**File**: `docker-compose.hybrid.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL with pgvector
  db:
    image: ankane/pgvector:latest
    container_name: bmadflow-db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-bmadflow}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
      POSTGRES_DB: ${POSTGRES_DB:-bmadflow}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-bmadflow}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - bmadflow-network

  # pgAdmin (Database Admin UI)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: bmadflow-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@bmadflow.local
      PGADMIN_DEFAULT_PASSWORD: admin
      PGADMIN_CONFIG_SERVER_MODE: 'False'
      PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED: 'False'
    ports:
      - "${PGADMIN_PORT:-5050}:80"
    depends_on:
      - db
    networks:
      - bmadflow-network

volumes:
  postgres_data:

networks:
  bmadflow-network:
    driver: bridge
```

### Deployment Steps (Hybrid)

**1. Start Docker Services**
```bash
# Start only database and pgAdmin
docker-compose -f docker-compose.hybrid.yml up -d
```

**2. Setup Backend**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend with hot reload
uvicorn app.main:app --reload --port 8000
```

**3. Setup Frontend (New Terminal)**
```bash
cd frontend

# Install dependencies
npm install

# Start frontend with hot reload
npm run dev
```

**4. Verify Services**
```bash
# Backend: http://localhost:8000/docs (Swagger UI)
# Frontend: http://localhost:3000
# pgAdmin: http://localhost:5050
```

---

## Database Migrations

### Alembic Workflow

**Generate Migration (after model changes):**
```bash
cd backend
alembic revision --autogenerate -m "Add new table or column"
```

**Review Generated Migration:**
```bash
# Check alembic/versions/<timestamp>_description.py
# Verify upgrade() and downgrade() functions
```

**Apply Migration:**
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>
```

**Rollback Migration:**
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

**View Migration History:**
```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

### Initial Migration

**File**: `alembic/versions/001_initial_schema.py`

Creates:
- `projects` table
- `project_docs` table
- `documents` table
- `llm_providers` table
- `conversations` table
- `messages` table

**File**: `alembic/versions/002_add_pgvector.py`

Creates:
- Enable pgvector extension
- `chunks` table with VECTOR(768) column
- HNSW index on embedding column

---

## Port Configuration

### Default Ports

| Service | Default Port | Environment Variable | Configurable |
|---------|--------------|----------------------|--------------|
| Frontend | 3000 | `FRONTEND_PORT` | ✅ |
| Backend | 8000 | `BACKEND_PORT` | ✅ |
| PostgreSQL | 5432 | `POSTGRES_PORT` | ✅ |
| pgAdmin | 5050 | `PGADMIN_PORT` | ✅ |
| Ollama | 11434 | `OLLAMA_ENDPOINT_URL` | ✅ (external service) |

### Resolving Port Conflicts

**Scenario**: Port 5432 already in use (existing PostgreSQL instance)

**Solution**: Change POSTGRES_PORT in `.env`
```bash
POSTGRES_PORT=5433
```

**Update DATABASE_URL accordingly**:
```bash
DATABASE_URL=postgresql+asyncpg://bmadflow:changeme@localhost:5433/bmadflow
```

---

## Data Persistence

### Docker Volumes

**PostgreSQL Data Volume:**
```yaml
volumes:
  postgres_data:  # Named volume for database persistence
```

**Location**: Docker managed volume (survives `docker-compose down`)

**View Volume:**
```bash
docker volume ls
docker volume inspect bmadflow_postgres_data
```

**Backup Database:**
```bash
# Export database to SQL file
docker exec bmadflow-db pg_dump -U bmadflow bmadflow > backup.sql

# Restore database from backup
docker exec -i bmadflow-db psql -U bmadflow bmadflow < backup.sql
```

**Delete Volume (WARNING: Deletes all data):**
```bash
docker-compose down -v
```

---

## Troubleshooting

### Backend Fails to Start

**Symptom**: Backend container exits immediately

**Check Logs:**
```bash
docker-compose logs backend
```

**Common Issues:**
1. **Database not ready**: Wait for `db` health check to pass
2. **Ollama unreachable**: Verify `OLLAMA_ENDPOINT_URL` is correct (use `host.docker.internal` in Docker)
3. **Environment variables missing**: Check `.env` file exists and is loaded

**Solution**: Restart services
```bash
docker-compose down
docker-compose up -d
```

### Frontend Cannot Reach Backend

**Symptom**: API calls fail with CORS errors

**Check**:
1. Backend is running: `curl http://localhost:8000/api/health`
2. CORS_ORIGINS environment variable includes frontend URL
3. Frontend `VITE_BACKEND_URL` is correct

**Fix CORS Configuration:**
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Must match frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### pgvector Extension Not Found

**Symptom**: `ERROR: extension "vector" does not exist`

**Solution**: Use `ankane/pgvector` Docker image (includes extension pre-installed)
```yaml
db:
  image: ankane/pgvector:latest  # NOT postgres:15
```

### Ollama Connection Refused

**Symptom**: Backend logs show "Connection refused to localhost:11434"

**Fix for Full Docker Mode:**
```bash
# Use host.docker.internal to reach host machine from container
OLLAMA_ENDPOINT_URL=http://host.docker.internal:11434
```

**Fix for Hybrid Mode:**
```bash
# Use localhost (backend runs on host)
OLLAMA_ENDPOINT_URL=http://localhost:11434
```

**Verify Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

---

## Performance Considerations

### Docker Resource Allocation

**Recommended Docker Desktop Settings:**
- CPUs: 4+
- Memory: 8GB+
- Swap: 2GB
- Disk: 50GB+

**Why**: PostgreSQL + pgvector + Ollama (host) + containers require adequate resources

### Hot Reload Performance

**Full Docker Mode:**
- Slower hot reload due to volume mounting overhead
- Use for testing full deployment

**Hybrid Mode:**
- Faster hot reload (native file system)
- Recommended for active development

---

## Security Considerations

### POC-Specific Shortcuts (NOT Production-Ready)

⚠️ **The following are acceptable ONLY for local POC deployment:**

1. **No pgAdmin Authentication**: `PGADMIN_CONFIG_SERVER_MODE: 'False'`
   - **Risk**: Unrestricted database access
   - **Mitigation**: Localhost-only, no network exposure

2. **Hardcoded Database Credentials**: `.env` file with simple passwords
   - **Risk**: Weak credentials
   - **Mitigation**: Local deployment only, not exposed to network

3. **No HTTPS/TLS**: HTTP-only communication
   - **Risk**: Unencrypted traffic
   - **Mitigation**: Localhost-only, no external network

4. **No API Authentication**: REST API has no auth layer
   - **Risk**: Unrestricted API access
   - **Mitigation**: Single-tenant POC, localhost-only

**Production Requirements (Out of Scope for POC):**
- API authentication (JWT, OAuth2)
- HTTPS/TLS certificates
- Secrets management (Vault, AWS Secrets Manager)
- Network security (VPC, firewall rules)
- Database connection encryption
- pgAdmin authentication

---

## Rollback Procedures

### Overview

Rollback procedures allow reverting to a previous working version when a deployment causes issues. For POC deployment, rollback is **manual** using Git tags and Docker Compose.

**Rollback Triggers:**
- Application crashes or fails to start after deployment
- Critical bugs introduced in new version
- Database migration causes data integrity issues
- Performance degradation beyond acceptable thresholds

---

### Pre-Deployment Best Practices

**1. Tag Stable Versions:**
```bash
# Before deploying changes, tag current working version
git tag -a v1.0.0 -m "Stable version before feature X"
git push origin v1.0.0
```

**2. Backup Database:**
```bash
# Always backup before migrations or major changes
docker exec bmadflow-db pg_dump -U bmadflow bmadflow > backup-$(date +%Y%m%d-%H%M%S).sql
```

**3. Document Changes:**
```bash
# Keep a deployment log
echo "$(date): Deployed feature X, migration 003_add_feature_x" >> deployment-log.txt
```

---

### Rollback Procedure (Full Docker Mode)

**Scenario**: Deployed version has critical bugs, need to revert to previous tag `v1.0.0`

**Step 1: Stop Current Deployment**
```bash
# Stop all services (preserves database data)
docker-compose down

# Verify all containers stopped
docker ps | grep bmadflow
```

**Step 2: Checkout Previous Version**
```bash
# Checkout previous stable tag
git checkout v1.0.0

# Verify correct version
git describe --tags
```

**Step 3: Rollback Database Migrations (if needed)**
```bash
# If new version ran migrations, roll them back
cd backend

# Check current migration
alembic current

# Rollback to previous migration (e.g., before feature X)
alembic downgrade <previous_revision_id>

# Example: Rollback one migration
alembic downgrade -1

# Verify rollback
alembic current
```

**Step 4: Rebuild and Restart Services**
```bash
# Rebuild Docker images with previous code
docker-compose build --no-cache

# Start services
docker-compose up -d

# Verify services are healthy
docker-compose ps
curl http://localhost:8000/api/health
```

**Step 5: Verify Rollback Success**
```bash
# Check logs for errors
docker-compose logs -f

# Test critical functionality
curl http://localhost:8000/api/projects
open http://localhost:3000

# If successful, tag as rollback version
git tag -a v1.0.0-rollback -m "Rollback from failed deployment"
```

---

### Rollback Procedure (Hybrid Mode)

**Step 1: Stop Local Processes**
```bash
# Stop backend (Ctrl+C in terminal or kill process)
pkill -f "uvicorn app.main:app"

# Stop frontend (Ctrl+C in terminal or kill process)
pkill -f "npm run dev"

# Stop Docker services
docker-compose -f docker-compose.hybrid.yml down
```

**Step 2: Checkout Previous Version**
```bash
git checkout v1.0.0
```

**Step 3: Rollback Database Migrations**
```bash
cd backend
source venv/bin/activate
alembic downgrade <previous_revision_id>
```

**Step 4: Reinstall Dependencies (if needed)**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

**Step 5: Restart Services**
```bash
# Start Docker services
docker-compose -f docker-compose.hybrid.yml up -d

# Start backend
cd backend
source venv/bin/activate
alembic upgrade head  # Apply correct migrations for this version
uvicorn app.main:app --reload --port 8000 &

# Start frontend
cd frontend
npm run dev &
```

---

### Database Rollback Scenarios

#### Scenario 1: Migration Failed Partially

**Symptom**: Migration script failed mid-execution, database in inconsistent state

**Solution**:
```bash
# 1. Restore from backup
docker exec -i bmadflow-db psql -U bmadflow bmadflow < backup-20250106-103000.sql

# 2. Verify data integrity
docker exec bmadflow-db psql -U bmadflow -d bmadflow -c "SELECT COUNT(*) FROM projects;"

# 3. Reset Alembic version to match restored database
alembic stamp <last_successful_revision_id>

# 4. Verify
alembic current
```

#### Scenario 2: Data Corruption After Migration

**Symptom**: Migration succeeded but data is corrupted or lost

**Solution**:
```bash
# 1. Stop all services immediately
docker-compose down

# 2. Drop corrupted database
docker exec bmadflow-db psql -U bmadflow -c "DROP DATABASE bmadflow;"

# 3. Recreate database
docker exec bmadflow-db psql -U bmadflow -c "CREATE DATABASE bmadflow;"

# 4. Restore from backup
docker exec -i bmadflow-db psql -U bmadflow bmadflow < backup-20250106-103000.sql

# 5. Enable pgvector extension
docker exec bmadflow-db psql -U bmadflow -d bmadflow -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 6. Reset Alembic to backup version
cd backend
alembic stamp <backup_revision_id>

# 7. Restart services with previous code version
git checkout v1.0.0
docker-compose up -d
```

---

### Emergency Rollback (Critical Production Issues)

**When to Use**: Application completely down, users unable to access system

**Quick Rollback (5 minutes):**
```bash
# 1. Immediate stop
docker-compose down

# 2. Restore last known good version
git checkout tags/v1.0.0

# 3. Restore database from last backup
docker-compose up -d db
sleep 10  # Wait for DB ready
docker exec -i bmadflow-db psql -U bmadflow bmadflow < last-known-good-backup.sql

# 4. Start services with previous version
docker-compose build --no-cache backend frontend
docker-compose up -d

# 5. Verify health
curl http://localhost:8000/api/health
```

---

### Rollback Checklist

**Before Rollback:**
- [ ] Document issue (screenshot, error logs, reproduction steps)
- [ ] Identify last known good version (Git tag)
- [ ] Locate corresponding database backup
- [ ] Notify team of rollback in progress (if applicable)
- [ ] Ensure Ollama service is running

**During Rollback:**
- [ ] Stop all services cleanly (`docker-compose down`)
- [ ] Checkout previous Git tag
- [ ] Rollback database migrations (if needed)
- [ ] Restore database from backup (if needed)
- [ ] Rebuild Docker images with `--no-cache`
- [ ] Start services and verify health

**After Rollback:**
- [ ] Verify critical functionality works
- [ ] Check logs for unexpected errors
- [ ] Test user flows (Browse, Sync, Chat)
- [ ] Document rollback in deployment log
- [ ] Create incident report (what went wrong, why rollback was needed)
- [ ] Plan fix for failed deployment

---

### Preventing Rollback Scenarios

**Best Practices:**

1. **Test Migrations Locally First:**
   ```bash
   # Test upgrade and downgrade before deploying
   alembic upgrade head
   alembic downgrade -1
   alembic upgrade head
   ```

2. **Use Reversible Migrations:**
   ```python
   # alembic/versions/003_add_feature.py
   def upgrade():
       op.add_column('projects', sa.Column('new_field', sa.String(255), nullable=True))

   def downgrade():
       op.drop_column('projects', 'new_field')  # Always define downgrade!
   ```

3. **Automated Backup Before Deployment:**
   ```bash
   # Add to deployment script
   #!/bin/bash
   BACKUP_FILE="backup-$(date +%Y%m%d-%H%M%S).sql"
   docker exec bmadflow-db pg_dump -U bmadflow bmadflow > $BACKUP_FILE
   echo "Backup created: $BACKUP_FILE"
   ```

4. **Health Check After Deployment:**
   ```bash
   # Deployment script should verify health
   docker-compose up -d
   sleep 10

   if ! curl -f http://localhost:8000/api/health; then
       echo "Health check failed! Rolling back..."
       ./rollback.sh
   fi
   ```

5. **Staged Rollout (Future):**
   - Deploy to staging environment first
   - Run automated test suite
   - Monitor for 24 hours before production

---

## Related Documentation

- **High Level Architecture**: [high-level-architecture.md](high-level-architecture.md)
- **Source Tree**: [source-tree.md](source-tree.md)
- **Development Workflow**: [development-workflow.md](development-workflow.md)
- **Database Migrations**: [database-schema.md](database-schema.md#migration-strategy)
- **Monitoring**: [monitoring.md](monitoring.md)
- **Docker Compose Patterns**: [/docs/context/deployment/docker-compose-patterns.md](../context/deployment/docker-compose-patterns.md)

---
