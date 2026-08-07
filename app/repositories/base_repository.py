"""
Base Repository

Provides common CRUD operations for all repositories.
"""

from typing import Generic, Type, TypeVar

from sqlalchemy.orm import Session

from app.models.base_model import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Generic repository providing common CRUD operations.
    """

    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def create(self, entity: T) -> T:
        """
        Save a new entity to the database.
        """

        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)

        return entity

    def get_by_id(self, entity_id: int) -> T | None:
        """
        Retrieve an entity by its primary key.
        """

        return self.session.get(self.model, entity_id)