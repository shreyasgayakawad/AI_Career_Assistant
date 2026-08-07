"""
Source Repository

Repository for Source database operations.
"""

from sqlalchemy.orm import Session

from app.models.source import Source
from app.repositories.base_repository import BaseRepository


class SourceRepository(BaseRepository[Source]):
    """
    Repository for Source entities.
    """

    def __init__(self, session: Session):
        super().__init__(Source, session)