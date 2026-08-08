"""
Test User Repository

Verifies user lookup by email.
"""

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.user import User
from app.repositories.user_repository import UserRepository


def main() -> None:
    """
    Test UserRepository operations.
    """

    session = SessionLocal()

    try:
        repository = UserRepository(session)

        email = "repository_test@example.com"

        existing_user = repository.get_by_email(email)

        if existing_user:
            session.delete(existing_user)
            session.commit()

        user = User(
            name="Repository Test User",
            email=email,
            password_hash="test_hash",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        print("=" * 50)
        print("User Repository Test")
        print("=" * 50)

        print()
        print(f"Created User ID : {user.id}")

        # Test existing user lookup.
        retrieved_user = repository.get_by_email(
            email,
        )

        if retrieved_user is None:
            raise RuntimeError(
                "Existing user could not be found by email."
            )

        if retrieved_user.id != user.id:
            raise RuntimeError(
                "Retrieved user ID does not match."
            )

        print(
            "Existing User Lookup : Passed"
        )

        # Test non-existing user lookup.
        missing_user = repository.get_by_email(
            "does_not_exist@example.com",
        )

        if missing_user is not None:
            raise RuntimeError(
                "Non-existing user was unexpectedly found."
            )

        print(
            "Missing User Lookup   : Passed"
        )

        print()
        print(
            "User repository test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()