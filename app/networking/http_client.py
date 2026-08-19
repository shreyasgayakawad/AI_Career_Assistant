"""
HTTP Client

Reusable HTTP client for HTML pages and JSON APIs.
"""

from typing import Any

import httpx


class HttpClient:
    """
    Simple HTTP client wrapper.
    """

    def __init__(self) -> None:
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "AI-Career-Assistant/1.0 "
                    "(https://github.com/your-repo)"
                )
            },
        )

    def get(self, url: str) -> str:
        """
        Send a GET request and return the response body as text.
        """

        response = self.client.get(url)
        response.raise_for_status()

        return response.text

    def get_json(self, url: str) -> dict[str, Any]:
        """
        Send a GET request and return the response as JSON.
        """

        response = self.client.get(url)
        response.raise_for_status()

        return response.json()

    def post_json(self, url: str, body: dict[str, Any]) -> dict[str, Any]:
        """
        Send a POST request with a JSON body and return the response as JSON.
        """

        response = self.client.post(url, json=body)
        response.raise_for_status()

        return response.json()

    def close(self) -> None:
        """
        Close the HTTP client.
        """

        self.client.close()