"""
Google OAuth Configuration

Defines the OpenID Connect authorization endpoint and builds the
Google authorization URL used to begin sign-in.
"""

from urllib.parse import urlencode

from app.config.settings import (
    GOOGLE_CLIENT_ID,
    GOOGLE_REDIRECT_URI,
    GOOGLE_SCOPES,
)


GOOGLE_AUTHORIZATION_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth"
)


def build_authorization_url(state: str) -> str:
    """
    Build the Google OpenID Connect authorization URL.
    """

    parameters = {
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": GOOGLE_SCOPES,
        "state": state,
    }

    return (
        f"{GOOGLE_AUTHORIZATION_URL}"
        f"?{urlencode(parameters)}"
    )
