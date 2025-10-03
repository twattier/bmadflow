"""Sync schemas for API request/response validation."""

from typing import Optional
from pydantic import BaseModel, Field


class SyncTaskResponse(BaseModel):
    """Schema for sync task initiation response."""

    sync_task_id: str = Field(..., description="Unique sync task identifier")
    message: str = Field(..., description="Status message")


class SyncStatusResponse(BaseModel):
    """Schema for sync status response."""

    status: str = Field(
        ..., description="Sync status: pending/in_progress/completed/failed"
    )
    processed_count: int = Field(0, description="Number of documents processed")
    total_count: int = Field(0, description="Total number of documents to process")
    error_message: Optional[str] = Field(
        None, description="Error message if sync failed"
    )
    retry_allowed: bool = Field(False, description="Whether retry is allowed")

    # Extraction phase tracking (Story 2.5)
    extraction_phase: Optional[str] = Field(
        None, description="Extraction phase: pending/extracting/completed"
    )
    extracted_count: int = Field(0, description="Number of documents extracted")
    extraction_failures: int = Field(0, description="Number of extraction failures")
