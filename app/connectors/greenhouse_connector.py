"""
Greenhouse Connector

Fetches jobs from the Greenhouse Job Board API.
"""

from datetime import datetime

from app.connectors.base_connector import BaseConnector
from app.dto.scraped_job import ScrapedJob


class GreenhouseConnector(BaseConnector):
    """
    Connector for Greenhouse-hosted job boards.
    """

    def __init__(self, company: str):
        super().__init__()
        self.company = company

    @property
    def source_name(self) -> str:
        return "Greenhouse"

    @property
    def api_url(self) -> str:
        """
        Greenhouse Job Board API endpoint.
        """
        return (
            f"https://boards-api.greenhouse.io/v1/boards/"
            f"{self.company}/jobs?content=true"
        )

    def fetch_jobs(self) -> list[ScrapedJob]:
        """
        Fetch jobs from the Greenhouse API.
        """

        data = self.http_client.get_json(self.api_url)

        jobs: list[ScrapedJob] = []

        for item in data.get("jobs", []):

            posted_date = None

            first_published = item.get("first_published")
            if first_published:
                try:
                    posted_date = datetime.fromisoformat(
                        first_published.replace("Z", "+00:00")
                    )
                except ValueError:
                    posted_date = None

            jobs.append(
                ScrapedJob(
                    company=item.get("company_name", ""),
                    title=item.get("title", ""),
                    location=item.get("location", {}).get("name", ""),
                    url=item.get("absolute_url", ""),
                    description=item.get("content", ""),
                    external_job_id=str(item.get("id")),
                    posted_date=posted_date,
                )
            )

        return jobs