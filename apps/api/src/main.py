from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.core.database import get_db, init_db, engine
from src.routes.projects import router as projects_router
from src.routes.documents import router as documents_router
from src.routes.epics import router as epics_router
from src.routes.relationships import router as relationships_router
from src.services.ollama_service import OllamaService

app = FastAPI(title="BMADFlow API", version="1.0.0")

# Configure CORS with dynamic frontend port from environment
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{FRONTEND_PORT}"],  # Frontend origin from .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(projects_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(epics_router, prefix="/api")
app.include_router(relationships_router, prefix="/api")


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
    """Health check endpoint with database and OLLAMA verification."""
    try:
        # Test database connection
        await db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Test OLLAMA service
    try:
        ollama_service = OllamaService()
        ollama_health = await ollama_service.health_check()
        ollama_status = {
            "status": ollama_health["status"],
            "model": ollama_health["model"],
            "model_loaded": ollama_health["model_loaded"],
        }
    except Exception as e:
        ollama_status = {"status": "error", "message": str(e)}

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "ollama": ollama_status,
    }
