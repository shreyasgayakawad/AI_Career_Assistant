"""
SmartRecruiters Connector

Fetches jobs from the SmartRecruiters Public Jobs API.

Unlike Greenhouse, Lever, and Ashby, the SmartRecruiters API paginates
results using offset-based pagination and must iterate through pages
to retrieve the full job list.
"""

from datetime import datetime

from app.connectors.base_connector import BaseConnector
from app.dto.scraped_job import ScrapedJob

# Maximum jobs per page allowed by the SmartRecruiters API.
_PAGE_SIZE = 100


class SmartRecruitersConnector(BaseConnector):
    """
    Connector for SmartRecruiters-hosted job boards.
    """

    def __init__(self, company: str):
        super().__init__()
        self.company = company

    @property
    def source_name(self) -> str:
        return "SmartRecruiters"

    def _api_url(self, offset: int = 0) -> str:
        """
        SmartRecruiters Postings API endpoint with pagination params.
        """
        return (
            f"https://api.smartrecruiters.com/v1/companies/"
            f"{self.company}/postings?limit={_PAGE_SIZE}&offset={offset}"
        )

    @staticmethod
    def _extract_location(location: object) -> str | None:
        """
        Extract the full location string from the SmartRecruiters location dict.
        """
        if not isinstance(location, dict):
            return None

        full_location = location.get("fullLocation")
        if isinstance(full_location, str) and full_location.strip():
            return full_location.strip()

        # Build fallback from city + country if fullLocation is absent
        parts = [
            location.get("city"),
            location.get("country"),
        ]
        parts = [str(p) for p in parts if p]
        return ", ".join(parts) if parts else None

    @staticmethod
    def _extract_work_mode(location: object) -> str | None:
        """
        Extract raw work mode hint from the SmartRecruiters location dict.

        SmartRecruiters provides explicit boolean flags 'remote' and 'hybrid'.
        The normalization service will classify the final work_mode value;
        this method passes a raw hint through to keep connector behavior
        consistent with the rest of the pipeline.
        """
        if not isinstance(location, dict):
            return None

        if location.get("remote") is True:
            return "Remote"

        if location.get("hybrid") is True:
            return "Hybrid"

        return None

    @staticmethod
    def _extract_posted_date(value: object) -> datetime | None:
        """
        Parse a SmartRecruiters ISO 8601 release timestamp.
        """
        if not isinstance(value, str) or not value:
            return None

        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00"),
            )
        except ValueError:
            return None

    def _build_job_url(self, job_id: object) -> str:
        """
        Construct the canonical public job posting URL.
        """
        if not isinstance(job_id, str) or not job_id:
            return ""

        return (
            f"https://jobs.smartrecruiters.com/{self.company}/{job_id}"
        )

    def fetch_jobs(self) -> list[ScrapedJob]:
        """
        Fetch all pages of jobs from the SmartRecruiters API.
        """
        jobs: list[ScrapedJob] = []
        offset = 0

        while True:
            data = self.http_client.get_json(
                self._api_url(offset=offset),
            )

            if not isinstance(data, dict):
                break

            total_found = data.get("totalFound", 0)
            content = data.get("content", [])

            if not isinstance(content, list) or not content:
                break

            for item in content:
                if not isinstance(item, dict):
                    continue

                location = item.get("location")
                job_id = item.get("id")

                jobs.append(
                    ScrapedJob(
                        company=self.company,
                        title=str(item.get("name", "")),
                        location=self._extract_location(location),
                        url=self._build_job_url(job_id),
                        work_mode=self._extract_work_mode(location),
                        description=None,
                        external_job_id=str(job_id) if job_id is not None else None,
                        salary=None,
                        posted_date=self._extract_posted_date(
                            item.get("releasedDate"),
                        ),
                    )
                )

            offset += len(content)

            if offset >= total_found:
                break

        return jobs
