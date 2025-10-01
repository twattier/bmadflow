# Error Handling Strategy

## Error Response Format

```typescript
interface ApiError {
  error: {
    code: string;           // "PROJECT_NOT_FOUND"
    message: string;        // Human-readable
    details?: object;       // Additional context
    timestamp: string;      // ISO 8601
    requestId: string;      // UUID for tracing
  };
}
```

## Frontend Error Handling

- Axios interceptor catches all API errors
- Log to Sentry with context
- Display user-friendly toast notifications
- React Query error state management
- Auto-retry with exponential backoff for network errors

## Backend Error Handling

- Global exception handler in FastAPI middleware
- Consistent ApiError format for all errors
- Request ID for tracing in logs
- Structured logging (JSON to stdout)

---
