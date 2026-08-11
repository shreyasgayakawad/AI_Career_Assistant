"""
User Repository

Repository for User database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User entities.
    """

    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        """
        Retrieve a user by email address.
        """

        statement = (
            select(User)
            .where(User.email == email)
        )

        return self.session.scalar(statement)

    def get_by_google_subject(
        self,
        google_subject: str,
    ) -> User | None:
        """
        Retrieve a user by their Google OpenID Connect subject.
        """

        statement = (
            select(User)
            .where(
                User.google_subject == google_subject,
            )
        )

        return self.session.scalar(statement)
