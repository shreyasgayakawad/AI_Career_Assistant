"""
Google Identity Service

Resolves verified Google identities to existing user accounts.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository


class GoogleIdentityService:
    """
    Resolve Google OpenID Connect identities for existing users.
    """

    def __init__(self, session: Session):
        self.session = session
        self.user_repository = UserRepository(session)

    def resolve_existing_user(
        self,
        *,
        google_subject: str,
        email: str,
        email_verified: bool,
    ) -> User:
        """
        Find an existing user and link their Google subject.

        An established subject is authoritative and resolves directly.
        A new subject may only be linked to an existing user when the
        Google-provided email has been verified.
        """

        normalized_subject = google_subject.strip()
        normalized_email = email.strip().lower()

        if not normalized_subject:
            raise ValueError(
                "Google subject is required."
            )

        if not normalized_email:
            raise ValueError(
                "Google email is required."
            )

        if not email_verified:
            raise ValueError(
                "Google email must be verified."
            )

        user = self.user_repository.get_by_google_subject(
            normalized_subject,
        )

        if user is not None:
            return user

        user = self.user_repository.get_by_email(
            normalized_email,
        )

        if user is None:
            raise ValueError(
                "No existing account matches this Google email."
            )

        if user.google_subject is not None:
            raise ValueError(
                "This account is already linked to Google."
            )

        user.google_subject = normalized_subject

        try:
            self.session.commit()

        except IntegrityError as exc:
            self.session.rollback()

            raise ValueError(
                "This Google account is already linked."
            ) from exc

        self.session.refresh(user)

        return user
