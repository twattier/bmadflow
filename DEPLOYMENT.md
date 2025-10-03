# BMAD Flow - Deployment Guide

## Prerequisites

- **Node.js** 18.17.0+
- **Python** 3.11+
- **Docker** & Docker Compose

## Configuration

Uses single `.env` file for all deployments:
- **Docker**: Uses values as-is (service name `postgres`)
- **Local**: Scripts automatically override DATABASE_URL to `127.0.0.1:5434`

## Quick Start

### Docker Deployment (Recommended)
```bash
./scripts/deploy-docker.sh
```

### Local Development
```bash
./scripts/deploy-local.sh
```

## Services

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8003
- **API Docs**: http://localhost:8003/docs
- **Database**: postgresql://bmadflow:bmadflow_dev@localhost:5434/bmadflow
- **PgAdmin**: http://localhost:5050 (admin@example.com / admin)

## Testing

```bash
# Backend health
curl http://localhost:8003/api/health

# Epics endpoint
curl "http://localhost:8003/api/epics?project_id=7e4d469f-dd82-42ab-93a1-bc240e175c29"

# Run backend tests
docker exec bmad-flow-backend python3 -m pytest tests/ -v
```

## Troubleshooting

### Port conflicts
```bash
# Kill process using port
lsof -ti:PORT | xargs kill -9
```

### Database connection issues
```bash
# Check Docker database
docker logs bmad-flow-postgres

# Test connection  
docker exec bmad-flow-postgres psql -U bmadflow -d bmadflow -c "SELECT 1"
```

### View logs
```bash
# Docker
docker logs bmad-flow-backend -f
docker logs bmad-flow-frontend -f

# Local
tail -f /tmp/bmad-backend.log
tail -f /tmp/bmad-frontend.log
```

## Stop Services

**Docker:**
```bash
cd infrastructure && docker-compose down
```

**Local:**
```bash
# Use PIDs from deployment output
kill <BACKEND_PID> <FRONTEND_PID>
cd infrastructure && docker-compose down
```
