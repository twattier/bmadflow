# Monitoring and Observability

## Monitoring Stack

- **Frontend:** Browser console errors, Sentry
- **Backend:** Prometheus + Grafana (Phase 2), Sentry
- **Error Tracking:** Sentry for both frontend and backend
- **Logging:** Python structured logging to stdout (Docker logs)

## Key Metrics

**Frontend:**
- Core Web Vitals (LCP, FID, CLS)
- JavaScript errors
- API response times

**Backend:**
- Request rate, error rate, response time
- Database query performance
- LLM extraction latency

---
