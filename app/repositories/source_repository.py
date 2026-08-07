"""
Source Repository

Repository for Source database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.source import Source
from app.repositories.base_repository import BaseRepository


class SourceRepository(BaseRepository[Source]):
    """
    Repository for Source entities.
    """

    def __init__(self, session: Session):
        super().__init__(Source, session)

    def get_by_name(self, name: str) -> Source | None:
        """
        Retrieve a source by its name.
        """

        statement = select(Source).where(Source.name == name)

        return self.session.scalar(statement)