"""Pydantic schemas for Message API."""

from pydantic import BaseModel, Field

from app.schemas.conversation import MessageResponse


class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    content: str = Field(..., min_length=1)


class SendMessageResponse(BaseModel):
    """Schema for send message API response."""

    user_message: MessageResponse
    assistant_message: MessageResponse
