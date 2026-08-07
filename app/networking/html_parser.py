"""
HTML Parser

Reusable HTML parser wrapper.
"""

from bs4 import BeautifulSoup


class HtmlParser:
    """
    Simple wrapper around BeautifulSoup.
    """

    @staticmethod
    def parse(html: str) -> BeautifulSoup:
        """
        Parse HTML into a BeautifulSoup object.
        """

        return BeautifulSoup(html, "html.parser")