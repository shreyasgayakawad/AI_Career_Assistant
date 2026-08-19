"""
Workday Connector

Fetches jobs from Workday-powered career sites (myworkdayjobs.com).

Unlike other connectors, Workday has no single endpoint format -- each
company's career site lives on its own Workday tenant, identified by
three separate pieces: a datacenter/server identifier (e.g. "wd5"), a
tenant name, and a career-site name.

The list endpoint (CXS API) is a POST with a JSON body, hard-capped at
20 results per page -- requesting a larger page size does not error,
it silently returns an empty result set instead. This connector fetches
list-view data only; the richer per-job detail endpoint (real posting
dates, full multi-location data) is a separate request per job and is
intentionally out of scope here, consistent with this connector's
"don't fabricate what the source doesn't cleanly provide" approach to
posted_date.
"""

import re
from typing import Any

from app.connectors.base_connector import BaseConnector
from app.dto.scraped_job import ScrapedJob

# Workday's list endpoint hard-caps at 20 results per page. Requesting
# more does not error -- it silently returns an empty jobPostings array.
_PAGE_SIZE = 20


class WorkdayConnector(BaseConnector):
    """
    Connector for Workday-hosted career sites.

    The constructor requires three explicit identifiers -- do not
    attempt to derive one from another, because different companies
    use different datacenter numbers with no discoverable pattern.
    """

    def __init__(self, wd_server: str, tenant: str, site: str):
        super().__init__()
        self.wd_server = wd_server
        self.tenant = tenant
        self.site = site

    @property
    def source_name(self) -> str:
        return "Workday"

    @property
    def _host(self) -> str:
        """
        The tenant's full Workday host, e.g. "hp.wd5.myworkdayjobs.com".
        """
        return f"{self.tenant}.{self.wd_server}.myworkdayjobs.com"

    def _api_url(self) -> str:
        """
        Workday CXS list-endpoint URL.

        The tenant appears twice: once in the subdomain (paired with
        the datacenter identifier), once again in the path.
        """
        return (
            f"https://{self._host}/wday/cxs/"
            f"{self.tenant}/{self.site}/jobs"
        )

    def _build_job_url(self, external_path: str) -> str:
        """
        Construct the public job posting URL from the response's
        externalPath field (e.g. "/job/Fort-Collins/Some-Title_R12345").
        """
        if not isinstance(external_path, str) or not external_path:
            return ""

        return f"https://{self._host}/{self.site}{external_path}"

    @staticmethod
    def _extract_external_job_id(
        bullet_fields: list[Any],
    ) -> str | None:
        """
        Best-effort extraction of a requisition ID from Workday's
        bulletFields array.

        This field is not reliable across tenants: some put a
        requisition ID here (e.g. "R-3164651"), some put a location
        string instead, and some omit the field entirely. Only accept
        values that look like a requisition ID; return None otherwise
        rather than guessing. This is not the primary duplicate-
        detection key regardless -- job_posting_exists() checks
        posting URL first, which every Workday posting has.
        """
        if not isinstance(bullet_fields, list) or not bullet_fields:
            return None

        first = bullet_fields[0]

        if not isinstance(first, str):
            return None

        candidate = first.strip()

        if re.fullmatch(r"R-?\d+", candidate):
            return candidate

        return None

    @staticmethod
    def _extract_title(job: dict[str, Any]) -> str:
        """Extract the job title from the response record."""
        title = job.get("title")
        return str(title).strip() if isinstance(title, str) else ""

    @staticmethod
    def _extract_location(job: dict[str, Any]) -> str | None:
        """
        Extract the location text from the response record.

        Workday's list view often returns a vague count like
        "2 Locations" rather than a resolvable place name for
        multi-office postings -- the real per-location strings only
        exist in a separate per-job detail endpoint this connector
        does not call. This is a known limitation of list-only
        fetching, not a bug.
        """
        location = job.get("locationsText")
        if isinstance(location, str) and location.strip():
            return location.strip()
        return None

    @staticmethod
    def _extract_work_mode(job: dict[str, Any]) -> str | None:
        """
        Extract the raw work-mode hint from the response, for
        normalization downstream.
        """
        remote_type = job.get("remoteType")
        if isinstance(remote_type, str) and remote_type.strip():
            return remote_type.strip()
        return None

    @staticmethod
    def _extract_posted_date(job: dict[str, Any]) -> None:
        """
        Always returns None.

        Workday's list endpoint returns a relative text string for
        posting date (e.g. "Posted 3 Days Ago", "Posted 30+ Days
        Ago"), not an absolute timestamp -- and "30+ Days Ago" is a
        floor, not an exact value. The real ISO date only exists in a
        separate per-job detail endpoint this connector does not call.
        Rather than approximate a real date from ambiguous relative
        text, this is left None consistently, matching this project's
        existing "don't fabricate what the source doesn't clearly
        provide" convention (see work_mode -> UNKNOWN).
        """
        return None

    def _fetch_page(self, offset: int) -> dict[str, Any]:
        """
        Fetch a single page of results from the Workday CXS list
        endpoint.
        """
        body = {
            "appliedFacets": {},
            "limit": _PAGE_SIZE,
            "offset": offset,
            "searchText": "",
        }

        return self.http_client.post_json(self._api_url(), body)

    def fetch_jobs(self) -> list[ScrapedJob]:
        """
        Fetch all pages of jobs from the Workday CXS list endpoint.

        Note: Workday provides no salary data in the list endpoint
        (or the detail endpoint this connector does not call), so
        salary is always None for this source.
        """
        jobs: list[ScrapedJob] = []
        offset = 0

        while True:
            data = self._fetch_page(offset)

            if not isinstance(data, dict):
                break

            job_postings = data.get("jobPostings")

            if not isinstance(job_postings, list) or not job_postings:
                break

            for job in job_postings:
                if not isinstance(job, dict):
                    continue

                external_path = job.get("externalPath") or ""
                bullet_fields = job.get("bulletFields") or []

                jobs.append(
                    ScrapedJob(
                        company=self.tenant,
                        title=self._extract_title(job),
                        location=self._extract_location(job),
                        url=self._build_job_url(external_path),
                        work_mode=self._extract_work_mode(job),
                        description=None,
                        external_job_id=self._extract_external_job_id(
                            bullet_fields,
                        ),
                        salary=None,
                        posted_date=self._extract_posted_date(job),
                    )
                )

            offset += len(job_postings)

            total = data.get("total")

            if isinstance(total, int) and offset >= total:
                break

        return jobs