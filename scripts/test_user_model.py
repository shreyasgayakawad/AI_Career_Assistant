"""
Test User Model

Verifies that users can be created and retrieved.
"""

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.user import User


def main() -> None:
    """
    Test User model persistence.
    """

    session = SessionLocal()

    try:
        email = "test@example.com"

        existing_user = (
            session.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_user:
            session.delete(existing_user)
            session.commit()

        user = User(
            name="Test User",
            email=email,
            password_hash="test_hash",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        print("=" * 50)
        print("User Model Test")
        print("=" * 50)

        print()
        print(f"User ID        : {user.id}")
        print(f"Name           : {user.name}")
        print(f"Email          : {user.email}")
        print(f"Password Hash  : {user.password_hash}")

        retrieved_user = session.get(
            User,
            user.id,
        )

        if retrieved_user is None:
            raise RuntimeError(
                "User could not be retrieved."
            )

        if retrieved_user.name != "Test User":
            raise RuntimeError(
                "Retrieved user name does not match."
            )

        if retrieved_user.email != email:
            raise RuntimeError(
                "Retrieved user email does not match."
            )

        print()
        print("User Creation   : Passed")
        print("User Retrieval  : Passed")

        print()
        print("User model test passed.")

    finally:
        session.close()


if __name__ == "__main__":
    main()