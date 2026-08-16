"""
Ashby Connector

Fetches jobs from the Ashby Job Board API.
"""

from datetime import datetime

from app.connectors.base_connector import BaseConnector
from app.dto.scraped_job import ScrapedJob


class AshbyConnector(BaseConnector):
    """
    Connector for Ashby-hosted job boards.
    """

    def __init__(self, company: str):
        super().__init__()
        self.company = company

    @property
    def source_name(self) -> str:
        return "Ashby"

    @property
    def api_url(self) -> str:
        """
        Ashby Posting API endpoint.
        """
        return f"https://api.ashbyhq.com/posting-api/job-board/{self.company}"

    @staticmethod
    def _extract_location(item: dict[str, object]) -> str | None:
        """
        Extract the location string from an Ashby job item.
        """
        location = item.get("location")
        if isinstance(location, str) and location.strip():
            return location.strip()
        return None

    @staticmethod
    def _extract_work_mode(item: dict[str, object]) -> str | None:
        """
        Extract workplace type from Ashby job data.

        Ashby provides both a structured 'workplaceType' field
        ('Remote', 'Hybrid', 'OnSite') and an 'isRemote' boolean.
        The raw string value is returned so the normalization service
        handles final classification — this keeps the connector consistent
        with the rest of the pipeline.
        """
        workplace_type = item.get("workplaceType")
        if isinstance(workplace_type, str) and workplace_type.strip():
            return workplace_type.strip()

        # Fall back to isRemote boolean hint for normalization
        is_remote = item.get("isRemote")
        if is_remote is True:
            return "Remote"

        return None

    @staticmethod
    def _extract_posted_date(value: object) -> datetime | None:
        """
        Parse an Ashby ISO 8601 publish timestamp.
        """
        if not isinstance(value, str) or not value:
            return None

        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00"),
            )
        except ValueError:
            return None

    def fetch_jobs(self) -> list[ScrapedJob]:
        """
        Fetch and map jobs from the Ashby API into ScrapedJob DTOs.
        """
        data = self.http_client.get_json(self.api_url)

        if not isinstance(data, dict):
            return []

        jobs: list[ScrapedJob] = []

        for item in data.get("jobs", []):
            if not isinstance(item, dict):
                continue

            job_id = item.get("id")

            description = (
                item.get("descriptionPlain")
                or item.get("descriptionHtml")
                or ""
            )

            jobs.append(
                ScrapedJob(
                    company=self.company,
                    title=str(item.get("title", "")),
                    location=self._extract_location(item),
                    url=str(item.get("jobUrl") or item.get("applyUrl") or ""),
                    work_mode=self._extract_work_mode(item),
                    description=str(description) if description else None,
                    external_job_id=str(job_id) if job_id is not None else None,
                    salary=None,
                    posted_date=self._extract_posted_date(item.get("publishedAt")),
                )
            )

        return jobs
