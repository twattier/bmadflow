# Backend Architecture

## Service Organization

```
apps/api/src/
├── routes/            # FastAPI route modules
├── services/          # Business logic (GitHubSyncService, LLMExtractionService, etc.)
├── repositories/      # Data access layer (BaseRepository, ProjectRepository, etc.)
├── models/            # SQLAlchemy ORM models
├── schemas/           # Pydantic request/response schemas
├── middleware/        # error_handler, request_logging, cors
├── core/              # config, database, redis, ollama
├── utils/             # Utilities
└── main.py            # FastAPI app entry
```

## Repository Pattern

```python
class BaseRepository(Generic[ModelType]):
    async def get_by_id(self, id: UUID) -> Optional[ModelType]: ...
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]: ...
    async def create(self, **kwargs) -> ModelType: ...
    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]: ...
    async def delete(self, id: UUID) -> bool: ...
```

## Authentication (Phase 2)

- **Method:** GitHub OAuth + JWT tokens
- **Token Storage:** httpOnly cookies
- **Session Management:** 30-min access token, 7-day refresh token
- **Middleware:** `get_current_user()` dependency for protected routes

---
