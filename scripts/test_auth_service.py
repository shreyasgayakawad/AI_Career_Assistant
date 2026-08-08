"""
Test Authentication Service

Verifies user registration, password hashing,
login, and authentication failure handling.
"""

import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService


def main() -> None:
    """
    Test AuthService registration and login.
    """

    session = SessionLocal()

    try:
        service = AuthService(session)

        email = "auth_test@example.com"
        password = "SecureTestPassword123!"

        # Clean up from a previous test run.
        existing_user = (
            session.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_user:
            session.delete(existing_user)
            session.commit()

        print("=" * 50)
        print("Authentication Service Test")
        print("=" * 50)

        # ---------------------------------------------------------
        # 1. Registration
        # ---------------------------------------------------------

        user = service.register_user(
            name="Auth Test User",
            email=email,
            password=password,
        )

        print()
        print(f"Created User ID : {user.id}")
        print(f"Name            : {user.name}")
        print(f"Email           : {user.email}")

        if user.email != email:
            raise RuntimeError(
                "Registered email does not match."
            )

        if user.name != "Auth Test User":
            raise RuntimeError(
                "Registered name does not match."
            )

        if user.password_hash == password:
            raise RuntimeError(
                "Password was stored as plain text."
            )

        if not user.password_hash.startswith(
            "scrypt$"
        ):
            raise RuntimeError(
                "Password was not stored using scrypt."
            )

        print()
        print("User Registration       : Passed")
        print("Password Hashing        : Passed")

        # ---------------------------------------------------------
        # 2. Successful login
        # ---------------------------------------------------------

        logged_in_user = service.login_user(
            email=email,
            password=password,
        )

        if logged_in_user.id != user.id:
            raise RuntimeError(
                "Logged-in user ID does not match."
            )

        print(
            "Successful Login       : Passed"
        )

        # ---------------------------------------------------------
        # 3. Wrong password
        # ---------------------------------------------------------

        try:
            service.login_user(
                email=email,
                password="WrongPassword123!",
            )

            raise RuntimeError(
                "Login succeeded with an incorrect password."
            )

        except ValueError as exc:
            if str(exc) != (
                "Invalid email or password."
            ):
                raise RuntimeError(
                    "Unexpected wrong-password error: "
                    f"{exc}"
                )

        print(
            "Wrong Password Rejected : Passed"
        )

        # ---------------------------------------------------------
        # 4. Unknown email
        # ---------------------------------------------------------

        try:
            service.login_user(
                email="does_not_exist@example.com",
                password=password,
            )

            raise RuntimeError(
                "Login succeeded for a non-existent user."
            )

        except ValueError as exc:
            if str(exc) != (
                "Invalid email or password."
            ):
                raise RuntimeError(
                    "Unexpected unknown-email error: "
                    f"{exc}"
                )

        print(
            "Unknown Email Rejected  : Passed"
        )

        # ---------------------------------------------------------
        # 5. Duplicate registration
        # ---------------------------------------------------------

        try:
            service.register_user(
                name="Duplicate Test User",
                email=email.upper(),
                password="AnotherPassword123!",
            )

            raise RuntimeError(
                "Duplicate account was created."
            )

        except ValueError as exc:
            if str(exc) != (
                "An account with this email already exists."
            ):
                raise RuntimeError(
                    "Unexpected duplicate-account error: "
                    f"{exc}"
                )

        print(
            "Duplicate Account Prevention : Passed"
        )

        print()
        print(
            "Authentication service test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()