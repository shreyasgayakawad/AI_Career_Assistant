"""
Authentication Dependencies

Provides FastAPI dependencies for authenticated users.
"""

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.jwt import decode_access_token
from app.config.settings import AUTH_COOKIE_NAME
from app.models.user import User


security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        security,
    ),
    browser_access_token: str | None = Cookie(
        default=None,
        alias=AUTH_COOKIE_NAME,
    ),
    session: Session = Depends(get_db),
) -> User:
    """
    Retrieve the authenticated user from the JWT.
    """

    token = (
        credentials.credentials
        if credentials is not None
        else browser_access_token
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

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
