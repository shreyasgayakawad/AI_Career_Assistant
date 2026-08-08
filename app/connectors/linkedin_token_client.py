"""
LinkedIn OAuth Token Client

Handles authorization-code exchange and LinkedIn OpenID Connect
UserInfo retrieval.
"""

import httpx

from app.config.settings import (
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET,
    LINKEDIN_REDIRECT_URI,
)
from app.connectors.linkedin_oauth import (
    LINKEDIN_TOKEN_URL,
    LINKEDIN_USERINFO_URL,
)


class LinkedInTokenClient:
    """
    Client for communicating with LinkedIn OAuth endpoints.
    """

    def exchange_code(
        self,
        code: str,
    ) -> dict:
        """
        Exchange a LinkedIn authorization code for tokens.
        """

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": LINKEDIN_CLIENT_ID,
            "client_secret": LINKEDIN_CLIENT_SECRET,
            "redirect_uri": LINKEDIN_REDIRECT_URI,
        }

        try:
            response = httpx.post(
                LINKEDIN_TOKEN_URL,
                data=payload,
                timeout=15.0,
            )
        except httpx.HTTPError as exc:
            raise ValueError(
                "Unable to connect to LinkedIn token endpoint."
            ) from exc

        if response.status_code != 200:
            raise ValueError(
                "LinkedIn token exchange failed."
            )

        try:
            token_data = response.json()
        except ValueError as exc:
            raise ValueError(
                "LinkedIn token response was invalid."
            ) from exc

        access_token = token_data.get(
            "access_token",
        )

        if not access_token:
            raise ValueError(
                "LinkedIn token response did not contain an access token."
            )

        return token_data

    def get_userinfo(
        self,
        access_token: str,
    ) -> dict:
        """
        Retrieve the authenticated LinkedIn member's OIDC profile.
        """

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = httpx.get(
                LINKEDIN_USERINFO_URL,
                headers=headers,
                timeout=15.0,
            )
        except httpx.HTTPError as exc:
            raise ValueError(
                "Unable to connect to LinkedIn UserInfo endpoint."
            ) from exc

        if response.status_code != 200:
            raise ValueError(
                "LinkedIn UserInfo request failed."
            )

        try:
            userinfo = response.json()
        except ValueError as exc:
            raise ValueError(
                "LinkedIn UserInfo response was invalid."
            ) from exc

        if not userinfo.get("sub"):
            raise ValueError(
                "LinkedIn UserInfo response did not contain a member ID."
            )

        return userinfo