"""
Authentication Service

Provides user registration and authentication.
"""

import base64
import hashlib
import hmac
import os

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """
    Business service for user authentication.
    """

    def __init__(self, session: Session):
        self.user_repository = UserRepository(session)
        self.session = session

    def _hash_password(
        self,
        password: str,
    ) -> str:
        """
        Hash a password using scrypt.
        """

        salt = os.urandom(16)

        password_hash = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=16384,
            r=8,
            p=1,
        )

        encoded_salt = base64.b64encode(
            salt,
        ).decode("utf-8")

        encoded_hash = base64.b64encode(
            password_hash,
        ).decode("utf-8")

        return (
            f"scrypt$"
            f"{encoded_salt}$"
            f"{encoded_hash}"
        )

    def _verify_password(
        self,
        password: str,
        stored_hash: str,
    ) -> bool:
        """
        Verify a password against a stored hash.
        """

        try:
            algorithm, encoded_salt, encoded_hash = (
                stored_hash.split("$")
            )

            if algorithm != "scrypt":
                return False

            salt = base64.b64decode(
                encoded_salt,
            )

            expected_hash = base64.b64decode(
                encoded_hash,
            )

            actual_hash = hashlib.scrypt(
                password.encode("utf-8"),
                salt=salt,
                n=16384,
                r=8,
                p=1,
            )

            return hmac.compare_digest(
                actual_hash,
                expected_hash,
            )

        except (ValueError, TypeError):
            return False

    def register_user(
        self,
        *,
        name: str,
        email: str,
        password: str,
    ) -> User:
        """
        Create a new user account.
        """

        normalized_email = email.strip().lower()

        existing_user = (
            self.user_repository.get_by_email(
                normalized_email,
            )
        )

        if existing_user is not None:
            raise ValueError(
                "An account with this email already exists."
            )

        if not name.strip():
            raise ValueError(
                "Name is required."
            )

        if not password:
            raise ValueError(
                "Password is required."
            )

        user = User(
            name=name.strip(),
            email=normalized_email,
            password_hash=self._hash_password(
                password,
            ),
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def login_user(
        self,
        *,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate a user by email and password.
        """

        normalized_email = email.strip().lower()

        user = self.user_repository.get_by_email(
            normalized_email,
        )

        if user is None:
            raise ValueError(
                "Invalid email or password."
            )

        if not self._verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError(
                "Invalid email or password."
            )

        return user