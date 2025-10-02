# BMADFlow

[![CI](https://github.com/twattier/bmadflow/actions/workflows/ci.yml/badge.svg)](https://github.com/twattier/bmadflow/actions/workflows/ci.yml)

Project management and documentation visualization tool for BMAD methodology.

## Prerequisites

- Docker 24.0+
- Node 20+
- Python 3.11+

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bmad-flow
   ```

2. **Setup environment variables**
   ```bash
   cp .env.example .env
   ```

   Optional: Edit `.env` to change ports if conflicts exist (e.g., `BACKEND_PORT=8001`)

3. **Start all services**
   ```bash
   cd infrastructure
   docker-compose up
   ```

4. **Verify setup**
   - Frontend: Open http://localhost:5173 in browser (or your configured `FRONTEND_PORT`)
   - Backend health check: `curl http://localhost:8000/api/health` (or your configured `BACKEND_PORT`)

   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-10-01T12:34:56.789012"
   }
   ```

## Troubleshooting

### Port Conflicts

If ports 5173, 8000, or 5432 are already in use:

1. Edit `.env` file:
   ```bash
   FRONTEND_PORT=5174
   BACKEND_PORT=8001
   POSTGRES_PORT=5433
   ```

2. Restart services:
   ```bash
   docker-compose down
   docker-compose up
   ```

### Docker Not Running

**Linux/WSL:**
```bash
sudo systemctl start docker
```

**macOS:**
- Open Docker Desktop application

**Windows:**
- Start Docker Desktop from Start menu

### Services Not Communicating

1. Check Docker network:
   ```bash
   docker network ls
   docker network inspect infrastructure_bmadflow-network
   ```

2. Verify all services are running:
   ```bash
   docker-compose ps
   ```

3. Check service logs:
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   docker-compose logs postgres
   ```

## Development

### Hot Reload

Both frontend and backend support hot reload:

- **Frontend**: Edit files in `apps/web/src/`, browser auto-refreshes
- **Backend**: Edit files in `apps/api/src/`, changes apply on next API call

### Running Tests

**Backend Tests:**
```bash
docker exec bmad-flow-backend pytest /app/tests/ -v
```

Current status: **66/66 tests passing** (100%)

### LLM Provider Configuration (Story 1.7)

**Selected Provider: OLLAMA (Local)**

BMADFlow uses OLLAMA for local LLM inference with privacy-first configuration:
- **Extraction Model**: `qwen2.5:3b` - Lightweight model for structured extraction
- **Embedding Model**: `nomic-embed-text` - 768-dimensional embeddings
- **Database Schema**: `vector(768)` for pgvector semantic search

**Rationale:** Privacy (40% weight), zero cost, sufficient capability for POC

⚠️ **Provider choice is PERMANENT** - Embedding dimension locked to 768d. Switching providers requires database migration.

See `scripts/llm-evaluation/` for provider evaluation framework and configuration details.

## Project Structure

```
bmadflow/
├── apps/
│   ├── web/          # React frontend (Vite + TypeScript)
│   └── api/          # FastAPI backend
├── infrastructure/   # Docker Compose configuration
├── docs/             # Project documentation
└── scripts/          # Utility scripts
```

## CI/CD Pipeline

This project uses GitHub Actions for automated testing and quality checks.

### Workflow Jobs

**Backend CI:**
- Black formatting check
- Ruff linting
- pytest with 50%+ coverage requirement
- PostgreSQL service container for tests

**Frontend CI:**
- ESLint checks
- TypeScript compilation
- Vitest unit tests
- Production build verification

Both jobs run in parallel and must pass before merging to `main`.

### Branch Protection Setup

**For Repository Administrators:**

1. Navigate to: **Settings** > **Branches**
2. Add branch protection rule for `main`
3. Enable: **"Require status checks to pass before merging"**
4. Select required checks:
   - `backend-ci`
   - `frontend-ci`
5. Enable: **"Require branches to be up to date before merging"**

### Troubleshooting CI Failures

**Backend Failures:**
- Database connection errors: Verify PostgreSQL service container health checks
- Missing environment variables: Check `DATABASE_URL`, `LLM_PROVIDER` settings
- Import errors: Verify `requirements.txt` installed correctly

**Frontend Failures:**
- Type errors: Run `npm run type-check` locally before pushing
- Linting errors: Run `npm run lint --fix` locally
- Build errors: Check for missing imports or incorrect paths

**Performance Issues:**
- Slow installs: Check if dependency caching is working (logs show "Cache restored successfully")
- Timeout errors: Default job timeout is 10 minutes

## License

[To be determined]
