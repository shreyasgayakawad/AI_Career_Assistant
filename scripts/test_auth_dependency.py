"""
Authentication Dependency Test

Tests JWT-based current-user resolution.
"""

import app.models  # noqa: F401

from fastapi import HTTPException

from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token
from app.database.session import SessionLocal
from app.models.user import User


def main() -> None:
    """
    Test get_current_user behavior.
    """

    session = SessionLocal()

    try:
        email = "dependency_test@example.com"

        # Clean up previous test user.
        existing_user = (
            session.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_user:
            session.delete(existing_user)
            session.commit()

        # Create a test user.
        user = User(
            name="Dependency Test User",
            email=email,
            password_hash="test_hash",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        print()
        print("# Authentication Dependency Test")
        print()

        # ---------------------------------------------------------
        # 1. Create JWT
        # ---------------------------------------------------------

        token = create_access_token(
            user_id=user.id,
        )

        print(
            "JWT Creation           : Passed"
        )

        # ---------------------------------------------------------
        # 2. Resolve current user
        # ---------------------------------------------------------

        from fastapi.security import (
            HTTPAuthorizationCredentials,
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token,
        )

        current_user = get_current_user(
            credentials=credentials,
            session=session,
        )

        if current_user.id != user.id:
            raise RuntimeError(
                "Resolved user ID does not match."
            )

        if current_user.email != user.email:
            raise RuntimeError(
                "Resolved user email does not match."
            )

        print(
            "Current User Resolution : Passed"
        )

        # ---------------------------------------------------------
        # 3. Invalid token
        # ---------------------------------------------------------

        invalid_credentials = (
            HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="invalid-token",
            )
        )

        try:
            get_current_user(
                credentials=invalid_credentials,
                session=session,
            )

            raise RuntimeError(
                "Invalid token was accepted."
            )

        except HTTPException as exc:
            if exc.status_code != 401:
                raise RuntimeError(
                    "Expected HTTP 401 for invalid token, "
                    f"got {exc.status_code}."
                )

        print(
            "Invalid Token Rejected  : Passed"
        )

        print()
        print(
            "Authentication dependency test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()