# Security and Performance

## Security Requirements

**Frontend:**
- CSP headers to prevent XSS
- DOMPurify sanitizes markdown HTML
- No sensitive data in localStorage (POC)

**Backend:**
- Pydantic validation for all inputs
- SQLAlchemy parameterized queries (SQL injection prevention)
- Nginx rate limiting: 10 req/sec per IP
- CORS: Explicit origin whitelist only

**Phase 2 Auth:**
- JWT tokens in httpOnly cookies
- 30-min access token expiry
- GitHub OAuth only

## Performance Optimization

**Frontend:**
- Bundle size: <300KB gzipped
- Route-based code splitting (React.lazy)
- React Query 5-min cache
- Image lazy loading

**Backend:**
- Response time: <500ms (documents list), <200ms (single document)
- Database indexes on frequently queried columns
- Redis caching: 5-min TTL, >80% hit rate target
- Connection pooling: 5 baseline, 10 max

---
