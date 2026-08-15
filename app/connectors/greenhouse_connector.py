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

    @staticmethod
    def _extract_work_mode(
        metadata: list[dict[str, object]] | None,
    ) -> str | None:
        """
        Extract the Greenhouse Location Type metadata value.

        Greenhouse exposes work mode through a custom metadata
        field named 'Location Type'.

        The raw value is returned for normalization.
        """

        if not metadata:
            return None

        for field in metadata:
            if not isinstance(field, dict):
                continue

            name = field.get("name")

            if not isinstance(name, str):
                continue

            if name.strip().lower() != "location type":
                continue

            value = field.get("value")

            if not isinstance(value, str):
                return None

            return value

        return None

    @staticmethod
    def _extract_posted_date(
        value: object,
    ) -> datetime | None:
        """
        Parse a Greenhouse publication timestamp.
        """

        if not isinstance(value, str) or not value:
            return None

        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00"),
            )
        except ValueError:
            return None

    @staticmethod
    def _extract_location(
        value: object,
    ) -> str | None:
        """
        Extract the Greenhouse location name safely.
        """

        if not isinstance(value, dict):
            return None

        name = value.get("name")

        if not isinstance(name, str):
            return None

        return name

    def fetch_jobs(self) -> list[ScrapedJob]:
        """
        Fetch jobs from the Greenhouse API.
        """

        data = self.http_client.get_json(
            self.api_url,
        )

        jobs: list[ScrapedJob] = []

        for item in data.get("jobs", []):
            if not isinstance(item, dict):
                continue

            metadata = item.get("metadata")

            if not isinstance(metadata, list):
                metadata = None

            jobs.append(
                ScrapedJob(
                    company=item.get(
                        "company_name",
                        "",
                    ),
                    title=item.get(
                        "title",
                        "",
                    ),
                    location=self._extract_location(
                        item.get("location"),
                    ),
                    url=item.get(
                        "absolute_url",
                        "",
                    ),
                    work_mode=self._extract_work_mode(
                        metadata,
                    ),
                    description=item.get(
                        "content",
                        "",
                    ),
                    external_job_id=(
                        str(item["id"])
                        if item.get("id") is not None
                        else None
                    ),
                    posted_date=self._extract_posted_date(
                        item.get("first_published"),
                    ),
                )
            )

        return jobs