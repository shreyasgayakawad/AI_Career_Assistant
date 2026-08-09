"""
OAuth State Repository

Repository for OAuth authorization state database operations.
"""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.oauth_state import OAuthState
from app.repositories.base_repository import BaseRepository


class OAuthStateRepository(
    BaseRepository[OAuthState]
):
    """
    Repository for OAuthState entities.
    """

    def __init__(
        self,
        session: Session,
    ):
        super().__init__(
            OAuthState,
            session,
        )

    def get_by_state(
        self,
        state: str,
    ) -> OAuthState | None:
        """
        Retrieve an OAuth state record by its state value.
        """

        statement = (
            select(OAuthState)
            .where(
                OAuthState.state == state,
            )
        )

        return self.session.scalar(statement)

    def get_by_user_and_platform(
        self,
        user_id: int,
        platform: str,
    ) -> OAuthState | None:
        """
        Retrieve a pending OAuth state for a user and platform.
        """

        statement = (
            select(OAuthState)
            .where(
                OAuthState.user_id == user_id,
                OAuthState.platform == platform,
            )
            .order_by(
                OAuthState.created_at.desc(),
            )
        )

        return self.session.scalar(statement)

    def delete(
        self,
        oauth_state: OAuthState,
    ) -> None:
        """
        Delete an OAuth state after successful validation.
        """

        self.session.delete(
            oauth_state,
        )
        self.session.commit()

    def consume(
        self,
        oauth_state: OAuthState,
    ) -> bool:
        """
        Atomically consume an OAuth state.

        Returns True when this operation deleted the state.
        Returns False when the state had already been consumed.
        """

        statement = (
            delete(OAuthState)
            .where(
                OAuthState.id == oauth_state.id,
            )
        )

        result = self.session.execute(
            statement,
        )

        self.session.commit()

        return result.rowcount == 1