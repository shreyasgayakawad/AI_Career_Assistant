"""
Google OAuth Routes

Provides the authorization endpoint for Google OpenID Connect login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.jwt import create_access_token
from app.config.settings import (
    AUTH_COOKIE_NAME,
    AUTH_COOKIE_SECURE,
    GOOGLE_ENABLED,
    GOOGLE_LOGIN_SUCCESS_REDIRECT_URI,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.services.google_oauth_service import GoogleOAuthService


router = APIRouter(
    prefix="/auth/google",
    tags=["Google OAuth"],
)


@router.get("/authorize")
def authorize_google(
    session: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Start the Google OpenID Connect authorization flow.
    """

    if not GOOGLE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google login is disabled.",
        )

    service = GoogleOAuthService(session)

    try:
        authorization_url = service.create_authorization_url()

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return RedirectResponse(
        url=authorization_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


@router.get("/callback")
def google_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    session: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Complete Google login and create the browser session cookie.
    """

    if not GOOGLE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google login is disabled.",
        )

    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google login state is missing.",
        )

    service = GoogleOAuthService(session)

    try:
        user = service.handle_callback(
            state=state,
            code=code,
            error=error,
            error_description=error_description,
        )

    except ValueError as exc:
        detail = str(exc)

        if detail in {
            "Invalid Google login state.",
            "Google login state has expired.",
            "Google authorization code is missing.",
            "Google ID token was invalid.",
            "Google ID token did not contain a subject.",
            "Google ID token did not contain an email.",
            "Google email must be verified.",
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail,
            ) from exc

        if detail.startswith("Google authorization failed."):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail,
            ) from exc

        if detail == "No existing account matches this Google email.":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        ) from exc

    response = RedirectResponse(
        url=GOOGLE_LOGIN_SUCCESS_REDIRECT_URI,
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=create_access_token(user.id),
        max_age=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite="lax",
    )

    return response
