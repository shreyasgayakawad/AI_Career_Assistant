"""
Browser Routes

Provides the minimal sign-in and session pages for local use.
"""

from html import escape

from fastapi import APIRouter, Cookie, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.jwt import decode_access_token
from app.config.settings import AUTH_COOKIE_NAME, GOOGLE_ENABLED
from app.models.user import User
from app.services.portal_connection_service import (
    PortalConnectionService,
)

router = APIRouter(tags=["Browser"])


@router.get("/", response_class=HTMLResponse)
def sign_in_page() -> HTMLResponse:
    """
    Render the browser sign-in page.
    """

    if GOOGLE_ENABLED:
        google_control = (
            '<a class="google-button" href="/auth/google/authorize">'
            "Continue with Google</a>"
        )
        status_message = "Use your Google account to continue."
    else:
        google_control = (
            '<button class="google-button" disabled>'
            "Continue with Google</button>"
        )
        status_message = "Google sign-in is being configured."

    return HTMLResponse(
        content=f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>AI Career Assistant</title>
          <style>
            body {{ font-family: Arial, sans-serif; background: #f7f8fc;
                   color: #172033; display: grid; min-height: 100vh;
                   margin: 0; place-items: center; }}
            main {{ background: white; border-radius: 16px; box-shadow:
                   0 10px 30px rgba(23, 32, 51, .12); max-width: 420px;
                   padding: 42px; text-align: center; }}
            h1 {{ margin: 0 0 12px; }}
            p {{ color: #596579; line-height: 1.5; }}
            .google-button {{ background: #1a73e8; border: 0;
                   border-radius: 8px; color: white; display: block;
                   font-size: 16px; margin-top: 28px; padding: 14px 20px;
                   text-decoration: none; width: 100%; box-sizing: border-box; }}
            button:disabled {{ background: #9aa8ba; cursor: not-allowed; }}
          </style>
        </head>
        <body>
          <main>
            <h1>AI Career Assistant</h1>
            <p>Sign in to view your connected job platforms.</p>
            {google_control}
            <p aria-live="polite">{status_message}</p>
          </main>
        </body>
        </html>
        """,
    )


@router.get(
    "/session",
    response_class=HTMLResponse,
    response_model=None,
)
def session_page(
    browser_access_token: str | None = Cookie(
        default=None,
        alias=AUTH_COOKIE_NAME,
    ),
    session: Session = Depends(get_db),
) -> HTMLResponse | RedirectResponse:
    """
    Render the signed-in user's connected-platform summary.
    """

    if not browser_access_token:
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    try:
        user_id = decode_access_token(browser_access_token)
    except ValueError:
        response = RedirectResponse(
            url="/",
            status_code=303,
        )
        response.delete_cookie(AUTH_COOKIE_NAME)
        return response

    user = session.get(User, user_id)

    if user is None:
        response = RedirectResponse(
            url="/",
            status_code=303,
        )
        response.delete_cookie(AUTH_COOKIE_NAME)
        return response

    service = PortalConnectionService(session)

    linkedin = service.get_connection(
        user.id,
        "LinkedIn",
    )

    linkedin_connected = bool(
        linkedin
        and linkedin.status == "ACTIVE"
        and linkedin.enabled
        and linkedin.credential_reference
    )

    linkedin_status = (
        "Connected"
        if linkedin_connected
        else "Not connected"
    )

    return HTMLResponse(
        content=f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Your session | AI Career Assistant</title>
          <style>
            body {{ font-family: Arial, sans-serif; background: #f7f8fc;
                   color: #172033; margin: 0; }}
            main {{ margin: 72px auto; max-width: 680px; padding: 32px; }}
            section {{ background: white; border-radius: 16px; box-shadow:
                   0 10px 30px rgba(23, 32, 51, .10); margin-top: 24px;
                   padding: 24px; }}
            .status {{ color: #147a43; font-weight: 700; }}
          </style>
        </head>
        <body>
          <main>
            <h1>Welcome, {escape(user.name)}</h1>
            <p>{escape(user.email)}</p>
            <section>
              <h2>LinkedIn</h2>
              <p class="status">{linkedin_status}</p>
            </section>
          </main>
        </body>
        </html>
        """,
    )