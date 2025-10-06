# BMADFlow Scripts

Service management scripts for BMADFlow deployment.

## Available Scripts

| Script | Description |
|--------|-------------|
| [`start_docker.sh`](start_docker.sh) | Deploy all services in Docker containers |
| [`start_local.sh`](start_local.sh) | Run frontend/backend locally with DB in Docker |
| [`stop_services.sh`](stop_services.sh) | Stop all services (Docker + local) |

## Quick Reference

```bash
# Docker deployment (production-like)
./scripts/start_docker.sh

# Local development (hot reload)
./scripts/start_local.sh

# Stop everything
./scripts/stop_services.sh
```

## Full Documentation

See [STARTUP_SCRIPTS.md](STARTUP_SCRIPTS.md) for:
- Detailed usage instructions
- Port configuration
- Troubleshooting guide
- Development workflows
- Environment setup

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local mode)
- Node.js 18+ (for local mode)
- `.env` file configured (copy from `.env.example`)

## Features

✅ Automatic port conflict detection and resolution
✅ Health checks for all services
✅ Color-coded status output
✅ Process management with PID tracking
✅ Comprehensive error handling

---

**Back to main README**: [../README.md](../README.md)
