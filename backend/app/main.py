"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health, hello
from app.config import settings
from app.routers import projects

app = FastAPI(
    title="BMADFlow API",
    description="Documentation hub for BMAD Method projects",
    version="0.1.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount API routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(hello.router, prefix="/api", tags=["hello"])
app.include_router(projects.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "BMADFlow API", "version": "0.1.0"}
