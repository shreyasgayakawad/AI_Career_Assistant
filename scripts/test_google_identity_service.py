"""
Test Google Identity Service

Verifies verified Google identities are linked only to matching
existing users.
"""

from uuid import uuid4

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.user import User
from app.services.google_identity_service import (
    GoogleIdentityService,
)


def main() -> None:
    """
    Test Google identity resolution and account-link protection.
    """

    session = SessionLocal()
    created_users: list[User] = []

    try:
        service = GoogleIdentityService(session)
        identifier = uuid4().hex

        user = User(
            name="Google Identity Test User",
            email=(
                f"google_identity_{identifier}@example.com"
            ),
            password_hash="test_hash",
        )
        linked_user = User(
            name="Already Linked Test User",
            email=(
                f"google_linked_{identifier}@example.com"
            ),
            password_hash="test_hash",
            google_subject=(
                f"google-linked-{identifier}"
            ),
        )

        session.add_all([user, linked_user])
        session.commit()
        session.refresh(user)
        session.refresh(linked_user)
        created_users.extend([user, linked_user])

        google_subject = f"google-subject-{identifier}"

        print("=" * 50)
        print("Google Identity Service Test")
        print("=" * 50)

        resolved_user = service.resolve_existing_user(
            google_subject=google_subject,
            email=user.email.upper(),
            email_verified=True,
        )

        if resolved_user.id != user.id:
            raise RuntimeError(
                "Google identity resolved to the wrong user."
            )

        if resolved_user.google_subject != google_subject:
            raise RuntimeError(
                "Google subject was not saved to the user."
            )

        print("Verified Email Link       : Passed")

        repeated_user = service.resolve_existing_user(
            google_subject=google_subject,
            email=linked_user.email,
            email_verified=True,
        )

        if repeated_user.id != user.id:
            raise RuntimeError(
                "Existing Google subject resolved incorrectly."
            )

        print("Existing Subject Lookup   : Passed")

        try:
            service.resolve_existing_user(
                google_subject=(
                    f"unverified-{identifier}"
                ),
                email=linked_user.email,
                email_verified=False,
            )

            raise RuntimeError(
                "Unverified Google email was accepted."
            )

        except ValueError as exc:
            if str(exc) != "Google email must be verified.":
                raise RuntimeError(
                    "Unexpected unverified-email error: "
                    f"{exc}"
                ) from exc

        if linked_user.google_subject != (
            f"google-linked-{identifier}"
        ):
            raise RuntimeError(
                "Unverified email changed an existing link."
            )

        print("Unverified Email Rejected : Passed")

        try:
            service.resolve_existing_user(
                google_subject=(
                    f"different-{identifier}"
                ),
                email=linked_user.email,
                email_verified=True,
            )

            raise RuntimeError(
                "Existing Google link was overwritten."
            )

        except ValueError as exc:
            if str(exc) != (
                "This account is already linked to Google."
            ):
                raise RuntimeError(
                    "Unexpected existing-link error: "
                    f"{exc}"
                ) from exc

        print("Existing Link Protected   : Passed")

        try:
            service.resolve_existing_user(
                google_subject=(
                    f"unknown-{identifier}"
                ),
                email=(
                    f"unknown_{identifier}@example.com"
                ),
                email_verified=True,
            )

            raise RuntimeError(
                "Unknown account was created from Google."
            )

        except ValueError as exc:
            if str(exc) != (
                "No existing account matches this Google email."
            ):
                raise RuntimeError(
                    "Unexpected unknown-account error: "
                    f"{exc}"
                ) from exc

        print("Unknown Account Rejected   : Passed")

        print()
        print("Google identity service test passed.")

    finally:
        for created_user in created_users:
            session.delete(created_user)

        session.commit()
        session.close()


if __name__ == "__main__":
    main()
