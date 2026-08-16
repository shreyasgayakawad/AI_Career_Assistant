"""
Lever Connector

Fetches jobs from the Lever Job Board API.
"""

from datetime import datetime, timezone

from app.connectors.base_connector import BaseConnector
from app.dto.scraped_job import ScrapedJob


class LeverConnector(BaseConnector):
    """
    Connector for Lever-hosted job boards.
    """

    def __init__(self, company: str):
        super().__init__()
        self.company = company

    @property
    def source_name(self) -> str:
        return "Lever"

    @property
    def api_url(self) -> str:
        """
        Lever Postings API endpoint.
        """
        return f"https://api.lever.co/v0/postings/{self.company}?mode=json"

    @staticmethod
    def _extract_location(categories: object) -> str | None:
        """
        Extract the location string safely from categories dict.
        """
        if not isinstance(categories, dict):
            return None

        location = categories.get("location")
        if isinstance(location, str) and location.strip():
            return location.strip()

        return None

    @staticmethod
    def _extract_posted_date(created_at: object) -> datetime | None:
        """
        Parse Lever epoch timestamp in milliseconds.
        """
        if isinstance(created_at, (int, float)) and created_at > 0:
            try:
                return datetime.fromtimestamp(
                    created_at / 1000.0,
                    tz=timezone.utc,
                )
            except (ValueError, OSError, OverflowError):
                return None
        return None

    @staticmethod
    def _extract_work_mode(item: dict[str, object]) -> str | None:
        """
        Extract raw workplace type or commitment hint.
        """
        workplace_type = item.get("workplaceType")
        if isinstance(workplace_type, str) and workplace_type.strip():
            return workplace_type.strip()

        return None

    def fetch_jobs(self) -> list[ScrapedJob]:
        """
        Fetch and map jobs from the Lever API into ScrapedJob DTOs.
        """
        data = self.http_client.get_json(self.api_url)

        if not isinstance(data, list):
            return []

        jobs: list[ScrapedJob] = []

        for item in data:
            if not isinstance(item, dict):
                continue

            categories = item.get("categories")
            job_id = item.get("id")

            # Extract description preference: plain text body, plain description, or raw HTML
            description = (
                item.get("descriptionPlain")
                or item.get("description")
                or item.get("descriptionBodyPlain")
                or ""
            )

            # Optional salary information
            salary = item.get("salaryDescription")
            if not isinstance(salary, str):
                salary = None

            jobs.append(
                ScrapedJob(
                    company=self.company,
                    title=str(item.get("text", "")),
                    location=self._extract_location(categories),
                    url=str(item.get("hostedUrl") or item.get("applyUrl") or ""),
                    work_mode=self._extract_work_mode(item),
                    description=str(description) if description else None,
                    external_job_id=str(job_id) if job_id is not None else None,
                    salary=salary,
                    posted_date=self._extract_posted_date(item.get("createdAt")),
                )
            )

        return jobs
