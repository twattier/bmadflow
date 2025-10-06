"""Hello endpoint demonstrating full-stack integration."""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/hello")
async def hello():
    """
    Hello endpoint demonstrating full-stack integration.
    Returns a welcome message with timestamp.
    """
    return {
        "message": "Hello BMADFlow",
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }
