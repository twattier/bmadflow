"""ProjectDoc Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ProjectDocCreate(BaseModel):
    """Schema for creating a new ProjectDoc."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    github_url: HttpUrl
    github_folder_path: Optional[str] = None

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, v: HttpUrl) -> HttpUrl:
        """Ensure URL is from github.com."""
        if v.host not in ["github.com", "www.github.com"]:
            raise ValueError("Must be a GitHub repository URL")
        return v

    @field_validator("github_folder_path")
    @classmethod
    def validate_folder_path(cls, v: Optional[str]) -> Optional[str]:
        """Normalize folder path (remove leading/trailing slashes)."""
        if v is None:
            return v
        return v.strip("/")


class ProjectDocUpdate(BaseModel):
    """Schema for updating a ProjectDoc."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    github_url: Optional[HttpUrl] = None
    github_folder_path: Optional[str] = None

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, v: Optional[HttpUrl]) -> Optional[HttpUrl]:
        """Ensure URL is from github.com."""
        if v is not None and v.host not in ["github.com", "www.github.com"]:
            raise ValueError("Must be a GitHub repository URL")
        return v

    @field_validator("github_folder_path")
    @classmethod
    def validate_folder_path(cls, v: Optional[str]) -> Optional[str]:
        """Normalize folder path (remove leading/trailing slashes)."""
        if v is None:
            return v
        return v.strip("/")


class ProjectDocResponse(BaseModel):
    """Schema for ProjectDoc API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    description: Optional[str]
    github_url: str
    github_folder_path: Optional[str]
    last_synced_at: Optional[datetime]
    last_github_commit_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class SyncResult(BaseModel):
    """Schema for sync operation result."""

    success: bool = Field(..., description="Whether sync completed successfully")
    files_synced: int = Field(..., ge=0, description="Number of files successfully synced")
    files_failed: int = Field(..., ge=0, description="Number of files that failed to sync")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    duration_seconds: float = Field(..., ge=0, description="Duration of sync operation in seconds")


class SyncStatusResponse(BaseModel):
    """Schema for sync status API response."""

    model_config = ConfigDict(from_attributes=True)

    status: Literal["idle", "syncing", "completed", "failed"] = Field(
        ..., description="Current sync status"
    )
    message: str = Field(..., description="Human-readable status message")
    last_synced_at: Optional[datetime] = Field(None, description="Timestamp of last sync")
    last_github_commit_date: Optional[datetime] = Field(
        None, description="Last commit date from GitHub for folder"
    )
