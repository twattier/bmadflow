# BMADFlow

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

Tests will be configured in Story 1.8 (CI/CD Pipeline).

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

## License

[To be determined]
