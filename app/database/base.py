"""
Database Base

Defines the SQLAlchemy Declarative Base used by all ORM models.

Every database model in AI Career Assistant should inherit from
the Base class defined in this module.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    """

    pass