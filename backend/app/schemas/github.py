"""GitHub API response schemas."""

from typing import Literal, Optional

from pydantic import BaseModel


class FileInfo(BaseModel):
    """GitHub file information from tree API."""

    path: str
    sha: str
    type: Literal["blob", "tree"]
    size: Optional[int] = None
