"""
Company Repository

Repository for Company database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """
    Repository for Company entities.
    """

    def __init__(self, session: Session):
        super().__init__(Company, session)

    def get_by_name(self, name: str) -> Company | None:
        """
        Retrieve a company by its name.
        """

        statement = select(Company).where(Company.name == name)

        return self.session.scalar(statement)