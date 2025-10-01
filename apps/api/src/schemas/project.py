"""Project schemas for API request/response validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    github_url: str = Field(..., description="GitHub repository URL")

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        """Validate that URL contains github.com."""
        if "github.com" not in v.lower():
            raise ValueError("URL must be a valid GitHub repository URL containing 'github.com'")
        return v


class ProjectResponse(BaseModel):
    """Schema for project API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    github_url: str
    last_sync_timestamp: Optional[datetime] = None
    sync_status: str = "idle"
    sync_progress: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
