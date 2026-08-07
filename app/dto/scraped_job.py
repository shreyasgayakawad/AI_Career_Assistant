"""
Scraped Job

Represents a job collected from any job source.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ScrapedJob:
    """
    Represents a scraped job before it is stored
    in the database.
    """

    company: str
    title: str
    location: str
    url: str
    description: str | None = None