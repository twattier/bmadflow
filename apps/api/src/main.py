from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, init_db, engine
from src.routes.projects import router as projects_router

app = FastAPI(title="BMADFlow API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(projects_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    await engine.dispose()


@app.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint with database connection verification."""
    try:
        # Test database connection
        await db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status
    }
