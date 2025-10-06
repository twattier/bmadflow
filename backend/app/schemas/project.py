"""Pydantic schemas for Project API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields optional)."""

    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema for project API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
