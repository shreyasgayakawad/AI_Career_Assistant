"""
LinkedIn OAuth Configuration

Defines the OAuth 2.0 / OpenID Connect endpoints and configuration
used by the LinkedIn integration.
"""

from urllib.parse import urlencode

from app.config.settings import (
    LINKEDIN_CLIENT_ID,
    LINKEDIN_REDIRECT_URI,
    LINKEDIN_SCOPES,
)


LINKEDIN_AUTHORIZATION_URL = (
    "https://www.linkedin.com/oauth/v2/authorization"
)

LINKEDIN_TOKEN_URL = (
    "https://www.linkedin.com/oauth/v2/accessToken"
)

LINKEDIN_USERINFO_URL = (
    "https://api.linkedin.com/v2/userinfo"
)


def build_authorization_url(
    state: str,
) -> str:
    """
    Build the LinkedIn OAuth authorization URL.
    """

    parameters = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "state": state,
        "scope": LINKEDIN_SCOPES,
    }

    return (
        f"{LINKEDIN_AUTHORIZATION_URL}"
        f"?{urlencode(parameters)}"
    )