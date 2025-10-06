# BMADFlow Startup Scripts

Three convenience scripts for managing BMADFlow services:

## Scripts Overview

| Script | Purpose | Environment |
|--------|---------|-------------|
| `start_docker.sh` | Deploy all services in Docker containers | Docker Compose |
| `start_local.sh` | Run frontend/backend locally, DB in Docker | Hybrid mode |
| `stop_services.sh` | Stop all services (Docker + local) | Both |

---

## 1. start_docker.sh

**Full Docker deployment** - All services in containers.

**Note**: Scripts automatically change to project root directory, so they work correctly whether run from project root or from `scripts/` directory.

### What it does:
1. Loads configuration from `.env`
2. Checks and stops any conflicting services (Docker or local)
3. Kills processes on required ports (3002, 8001, 5434, 5050)
4. Builds and starts all Docker containers
5. Verifies services are healthy

### Usage:
```bash
./start_docker.sh
```

### Services started:
- **Frontend**: http://localhost:3002 (React + Vite in container)
- **Backend**: http://localhost:8001 (FastAPI in container)
- **Database**: PostgreSQL on port 5434 (Docker)
- **pgAdmin**: http://localhost:5050 (Docker)

### When to use:
- Production-like environment
- Clean isolated deployment
- CI/CD simulation
- Quick demo setup

---

## 2. start_local.sh

**Hybrid deployment** - Frontend/backend local, DB in Docker.

### What it does:
1. Loads configuration from `.env`
2. Stops any conflicting Docker containers (keeps DB/pgAdmin running)
3. Kills local processes on frontend/backend ports
4. Starts PostgreSQL and pgAdmin in Docker
5. Installs dependencies (if needed)
6. Runs database migrations
7. Starts backend locally (background process)
8. Starts frontend locally (background process)
9. Saves PIDs to `.backend.pid` and `.frontend.pid`

### Usage:
```bash
./start_local.sh
```

### Prerequisites:
- Python 3.11+ (`python3 --version`)
- Node.js 18+ (`node --version`)
- Docker for database

### Services started:
- **Frontend**: http://localhost:3002 (local Vite dev server)
- **Backend**: http://localhost:8001 (local uvicorn with hot reload)
- **Database**: PostgreSQL on port 5434 (Docker)
- **pgAdmin**: http://localhost:5050 (Docker)

### Logs:
- Backend: `backend.log`
- Frontend: `frontend.log`
- View live: `tail -f backend.log frontend.log`

### When to use:
- Active development with hot reload
- Debugging backend/frontend code
- Testing without Docker overhead
- IDE integration (breakpoints, etc.)

---

## 3. stop_services.sh

**Stop all services** - Cleanly shuts down Docker and local services.

### What it does:
1. Stops all Docker containers (`docker-compose down`)
2. Kills local backend process (via `.backend.pid`)
3. Kills local frontend process (via `.frontend.pid`)
4. Force-kills any remaining processes on ports 3002, 8001
5. Cleans up PID files

### Usage:
```bash
./stop_services.sh
```

### When to use:
- Switch between Docker and local mode
- Clean shutdown before system maintenance
- Reset environment after testing
- Free up ports for other projects

---

## Port Configuration

All ports are defined in `.env`:

```bash
FRONTEND_PORT=3002
BACKEND_PORT=8001
POSTGRES_PORT=5434
PGADMIN_PORT=5050
```

**Important**: Scripts automatically detect and handle port conflicts by:
1. Checking if ports are in use
2. Stopping conflicting Docker containers
3. Killing processes using required ports

---

## Troubleshooting

### "Port already in use"
Scripts automatically kill conflicting processes. If manual intervention needed:
```bash
# Find process on port
lsof -i :3002
# Kill process
kill -9 <PID>
```

### "Database connection refused"
```bash
# Check database is running
docker-compose ps db
# View database logs
docker-compose logs db
```

### "Backend not responding"
For local mode, check logs:
```bash
tail -f backend.log
# Check if virtual environment is activated
source backend/.venv/bin/activate
```

### "Frontend build errors"
```bash
# Clean install dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Start fresh
```bash
./stop_services.sh
docker-compose down -v  # Remove volumes
./start_docker.sh       # or ./start_local.sh
```

---

## Development Workflow Examples

### Quick Start (Docker)
```bash
./start_docker.sh
# Access http://localhost:3002
# Stop: ./stop_services.sh
```

### Development Mode (Local)
```bash
./start_local.sh
# Code with hot reload
# Logs: tail -f backend.log frontend.log
# Stop: ./stop_services.sh
```

### Switch from Docker to Local
```bash
./stop_services.sh      # Stop Docker
./start_local.sh        # Start local
```

### Switch from Local to Docker
```bash
./stop_services.sh      # Stop local
./start_docker.sh       # Start Docker
```

### Run E2E Tests
```bash
# Ensure services are running
./start_docker.sh  # or ./start_local.sh

# Run tests
cd frontend
npm run test:e2e

# View report
npx playwright show-report
```

---

## Script Features

✅ **Automatic conflict resolution** - Detects and stops conflicting services
✅ **Port validation** - Checks all required ports from `.env`
✅ **Health checks** - Verifies services are responding
✅ **Color-coded output** - Green (success), Yellow (warning), Red (error)
✅ **Error handling** - Exits on failure with clear messages
✅ **Process management** - Saves PIDs for clean shutdown
✅ **Log capture** - Background processes log to files

---

## Environment Variables

Create `.env` from `.env.example`:
```bash
cp .env.example .env
```

Required variables:
- `FRONTEND_PORT` - Frontend dev server port
- `BACKEND_PORT` - Backend API port
- `POSTGRES_PORT` - PostgreSQL port
- `PGADMIN_PORT` - pgAdmin web UI port
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
