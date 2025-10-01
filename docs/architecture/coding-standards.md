# Coding Standards

## Critical Rules

- **Type Sharing:** Define types in `packages/shared/`, import as `@bmadflow/shared/types`
- **API Calls:** Use service layer + React Query hooks, never direct `fetch()`
- **Environment Variables:** Access via config objects only
- **Error Handling:** Use standard ApiError format
- **State Updates:** Never mutate state directly
- **Database Queries:** Always use repository pattern
- **Async/Await:** Use `async/await`, never `.then()` chains

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| React Components | PascalCase | `DocumentCard.tsx` |
| Hooks | camelCase + 'use' | `useProjects.ts` |
| API Routes | kebab-case | `/api/sync-status` |
| Python Functions | snake_case | `sync_repository()` |
| Database Tables | snake_case plural | `extracted_epics` |
| Constants | SCREAMING_SNAKE_CASE | `API_TIMEOUT` |

---
