"""SQLAlchemy database models."""

import uuid
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# Import all models here for alembic autogenerate
from .project import Project  # noqa: E402, F401
from .document import Document  # noqa: E402, F401
from .relationship import Relationship  # noqa: E402, F401
