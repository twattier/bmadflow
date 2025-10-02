"""SQLAlchemy database models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# Import all models here for alembic autogenerate
from .project import Project  # noqa: E402, F401
from .document import Document  # noqa: E402, F401
from .relationship import Relationship  # noqa: E402, F401
