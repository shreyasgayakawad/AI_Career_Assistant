"""
JWT Authentication Utilities

Provides JWT access-token creation and decoding.
"""

from datetime import datetime, timedelta, timezone

import jwt


# Temporary development configuration.
# We will move the secret to environment configuration
# before this is used outside local development.
SECRET_KEY = "change-this-development-secret-key-32"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


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
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
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
            SECRET_KEY,
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