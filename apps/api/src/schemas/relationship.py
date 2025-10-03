"""Relationship schemas for API request/response validation."""

from typing import List, Literal
from uuid import UUID
from pydantic import BaseModel


class NodeSchema(BaseModel):
    """Node in the relationship graph (epic or story)."""

    id: UUID
    title: str
    type: Literal["epic", "story"]
    status: str
    document_id: UUID


class EdgeSchema(BaseModel):
    """Edge in the relationship graph."""

    source_id: UUID
    target_id: UUID
    type: str  # "contains", "relates_to", "depends_on"


class GraphDataResponse(BaseModel):
    """Response schema for epic-story relationship graph."""

    nodes: List[NodeSchema]
    edges: List[EdgeSchema]
