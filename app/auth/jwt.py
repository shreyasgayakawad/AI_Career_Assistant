"""
JWT Authentication Utilities

Provides JWT access-token creation and decoding.
"""

from datetime import datetime, timedelta, timezone

import jwt

from app.config.settings import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_SECRET_KEY,
)


ALGORITHM = "HS256"


def create_access_token(
    user_id: int,
) -> str:
    """
    Create a JWT access token for a user.
    """

    now = datetime.now(timezone.utc)

    expires_at = (
        now
        + timedelta(
            minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> int:
    """
    Decode and validate a JWT access token.

    Returns the user ID stored in the token.
    """

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except jwt.PyJWTError as exc:
        raise ValueError(
            "Invalid or expired access token."
        ) from exc

    subject = payload.get("sub")

    if subject is None:
        raise ValueError(
            "Invalid access token."
        )

    try:
        return int(subject)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Invalid access token."
        ) from exc