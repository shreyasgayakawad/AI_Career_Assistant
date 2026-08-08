"""
Authentication API Test

Tests user registration, login, JWT generation,
and authentication failure handling.
"""

import app.models  # noqa: F401

from fastapi import HTTPException

from app.api.routes.auth import (
    LoginRequest,
    RegisterRequest,
    login,
    register,
)
from app.auth.jwt import decode_access_token
from app.database.session import SessionLocal
from app.models.user import User


def main() -> None:
    """
    Test authentication API behavior.
    """

    session = SessionLocal()

    try:
        email = "api_test@example.com"
        password = "SecureApiPassword123!"

        # Clean up previous test user.
        existing_user = (
            session.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_user:
            session.delete(existing_user)
            session.commit()

        print()
        print("# Authentication API Test")
        print()

        # ---------------------------------------------------------
        # 1. Registration
        # ---------------------------------------------------------

        register_response = register(
            request=RegisterRequest(
                name="API Test User",
                email=email,
                password=password,
            ),
            session=session,
        )

        print(f"User ID : {register_response.id}")
        print(f"Name    : {register_response.name}")
        print(f"Email   : {register_response.email}")

        if register_response.name != "API Test User":
            raise RuntimeError(
                "Registration returned incorrect name."
            )

        if register_response.email != email:
            raise RuntimeError(
                "Registration returned incorrect email."
            )

        user = session.get(
            User,
            register_response.id,
        )

        if user is None:
            raise RuntimeError(
                "Registered user was not saved."
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
        print("Registration API       : Passed")
        print("Password Protection    : Passed")

        # ---------------------------------------------------------
        # 2. Successful login
        # ---------------------------------------------------------

        login_response = login(
            request=LoginRequest(
                email=email,
                password=password,
            ),
            session=session,
        )

        if login_response.id != user.id:
            raise RuntimeError(
                "Login returned incorrect user ID."
            )

        if login_response.name != user.name:
            raise RuntimeError(
                "Login returned incorrect user name."
            )

        if login_response.email != user.email:
            raise RuntimeError(
                "Login returned incorrect email."
            )

        if not login_response.access_token:
            raise RuntimeError(
                "Login did not return an access token."
            )

        if login_response.token_type != "bearer":
            raise RuntimeError(
                "Unexpected token type."
            )

        print(
            "Successful Login       : Passed"
        )

        # ---------------------------------------------------------
        # 3. Verify JWT
        # ---------------------------------------------------------

        decoded_user_id = decode_access_token(
            login_response.access_token,
        )

        if decoded_user_id != user.id:
            raise RuntimeError(
                "JWT contains the wrong user ID."
            )

        print(
            "JWT Generation         : Passed"
        )

        print(
            "JWT User Verification  : Passed"
        )

        # ---------------------------------------------------------
        # 4. Wrong password
        # ---------------------------------------------------------

        try:
            login(
                request=LoginRequest(
                    email=email,
                    password="WrongPassword123!",
                ),
                session=session,
            )

            raise RuntimeError(
                "Login succeeded with an incorrect password."
            )

        except HTTPException as exc:
            if exc.status_code != 401:
                raise RuntimeError(
                    "Expected HTTP 401 for wrong password, "
                    f"got {exc.status_code}."
                )

            if exc.detail != (
                "Invalid email or password."
            ):
                raise RuntimeError(
                    "Unexpected wrong-password error."
                )

        print(
            "Wrong Password Rejected : Passed"
        )

        # ---------------------------------------------------------
        # 5. Unknown email
        # ---------------------------------------------------------

        try:
            login(
                request=LoginRequest(
                    email="unknown@example.com",
                    password=password,
                ),
                session=session,
            )

            raise RuntimeError(
                "Login succeeded for an unknown email."
            )

        except HTTPException as exc:
            if exc.status_code != 401:
                raise RuntimeError(
                    "Expected HTTP 401 for unknown email, "
                    f"got {exc.status_code}."
                )

            if exc.detail != (
                "Invalid email or password."
            ):
                raise RuntimeError(
                    "Unexpected unknown-email error."
                )

        print(
            "Unknown Email Rejected  : Passed"
        )

        # ---------------------------------------------------------
        # 6. Duplicate registration
        # ---------------------------------------------------------

        try:
            register(
                request=RegisterRequest(
                    name="Duplicate User",
                    email=email.upper(),
                    password="AnotherPassword123!",
                ),
                session=session,
            )

            raise RuntimeError(
                "Duplicate account was created."
            )

        except HTTPException as exc:
            if exc.status_code != 400:
                raise RuntimeError(
                    "Expected HTTP 400 for duplicate "
                    f"registration, got {exc.status_code}."
                )

        print(
            "Duplicate Registration  : Passed"
        )

        print()
        print(
            "Authentication API test passed."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()