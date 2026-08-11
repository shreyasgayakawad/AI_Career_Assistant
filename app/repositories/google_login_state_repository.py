"""
Google Login State Repository

Repository for temporary Google sign-in OAuth state records.
"""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.google_login_state import GoogleLoginState
from app.repositories.base_repository import BaseRepository


class GoogleLoginStateRepository(
    BaseRepository[GoogleLoginState]
):
    """
    Repository for GoogleLoginState entities.
    """

    def __init__(self, session: Session):
        super().__init__(GoogleLoginState, session)

    def get_by_state(
        self,
        state: str,
    ) -> GoogleLoginState | None:
        """
        Retrieve a pending Google login state by value.
        """

        statement = (
            select(GoogleLoginState)
            .where(GoogleLoginState.state == state)
        )

        return self.session.scalar(statement)

    def consume(
        self,
        google_login_state: GoogleLoginState,
    ) -> bool:
        """
        Atomically consume a Google login state.

        Returns True only when the state was deleted.
        """

        statement = (
            delete(GoogleLoginState)
            .where(
                GoogleLoginState.id == google_login_state.id,
            )
        )

        result = self.session.execute(statement)
        self.session.commit()

        return result.rowcount == 1
