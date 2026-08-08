"""
Authentication Dependencies

Provides FastAPI dependencies for authenticated users.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.jwt import decode_access_token
from app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security,
    ),
    session: Session = Depends(get_db),
) -> User:
    """
    Retrieve the authenticated user from the JWT.
    """

    token = credentials.credentials

    try:
        user_id = decode_access_token(token)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    user = session.get(
        User,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user