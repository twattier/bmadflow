# Deployment Architecture

## Deployment Strategy

**Frontend:**
- Docker container with Nginx serving static build (`npm run build`)
- Build output: `apps/web/dist/`
- Phase 2: CDN (Cloudflare)

**Backend:**
- Docker container with uvicorn + FastAPI
- Phase 2: Kubernetes with Helm charts

**Database:**
- PostgreSQL Docker container (POC)
- Phase 2: Managed PostgreSQL (AWS RDS, GCP Cloud SQL)

**OLLAMA:**
- External server (existing GPU-enabled infrastructure)
- FastAPI backend connects via HTTP API
- No deployment needed (uses existing server)

## CI/CD Pipeline

GitHub Actions workflow:
1. **Frontend Tests:** ESLint, Vitest, build check
2. **Backend Tests:** Black, Ruff, pytest with coverage
3. **Accessibility Audit:** Lighthouse CI (score ≥90)
4. **Deploy:** (Phase 2) Deploy to production on main branch merge

## Environments

| Environment | Frontend | Backend | Purpose |
|-------------|----------|---------|---------|
| Development | localhost:5173 | localhost:8000 | Local dev |
| Production | bmadflow.internal | api.bmadflow.internal | Live |

---
