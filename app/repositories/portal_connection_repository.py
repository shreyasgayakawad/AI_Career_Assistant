"""
Portal Connection Repository

Repository for PortalConnection database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.portal_connection import PortalConnection
from app.repositories.base_repository import BaseRepository


class PortalConnectionRepository(
    BaseRepository[PortalConnection]
):
    """
    Repository for PortalConnection entities.
    """

    def __init__(self, session: Session):
        super().__init__(
            PortalConnection,
            session,
        )

    def get_by_user_and_platform(
        self,
        user_id: int,
        platform: str,
    ) -> PortalConnection | None:
        """
        Retrieve a user's connection for a specific platform.
        """

        statement = (
            select(PortalConnection)
            .where(
                PortalConnection.user_id == user_id,
                PortalConnection.platform == platform,
            )
        )

        return self.session.scalar(statement)

    def get_all_for_user(
        self,
        user_id: int,
    ) -> list[PortalConnection]:
        """
        Retrieve all portal connections belonging to a user.
        """

        statement = (
            select(PortalConnection)
            .where(
                PortalConnection.user_id == user_id,
            )
            .order_by(
                PortalConnection.platform.asc(),
            )
        )

        return list(
            self.session.scalars(statement).all()
        )