from fastapi import FastAPI, Depends
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, init_db, engine

app = FastAPI()


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
