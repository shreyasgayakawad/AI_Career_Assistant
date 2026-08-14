"""
Scraped Job

Represents a job collected from any job source.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ScrapedJob:
    """
    Represents a scraped job before it is stored
    in the database.
    """

    company: str
    title: str
    location: str | None
    url: str

    work_mode: str | None = None
    description: str | None = None
    external_job_id: str | None = None
    salary: str | None = None
    posted_date: datetime | None = None