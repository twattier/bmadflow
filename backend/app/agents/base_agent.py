"""Base agent class for Pydantic agent framework."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class BaseAgent(BaseModel, ABC):
    """Abstract base class for all agents.

    Agents are Pydantic models that encapsulate business logic for
    complex workflows involving LLM calls and tool interactions.

    Attributes:
        project_id: UUID of the project this agent operates on
        conversation_id: UUID of the conversation context
    """

    project_id: UUID = Field(..., description="Project UUID")
    conversation_id: UUID = Field(..., description="Conversation UUID")

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    @abstractmethod
    async def process_query(self, user_message: str) -> Dict[str, Any]:
        """Process a user query and return a structured response.

        Args:
            user_message: User's input message

        Returns:
            Dictionary containing response data (structure varies by agent)

        Raises:
            Exception: Implementation-specific exceptions
        """
        pass
