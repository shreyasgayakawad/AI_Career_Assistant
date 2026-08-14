"""
Job Normalization Service

Normalizes scraped job data before persistence.
"""

from app.dto.scraped_job import ScrapedJob


class JobNormalizationService:
    """
    Normalizes incoming ScrapedJob objects.
    """

    ALLOWED_WORK_MODES = {
        "REMOTE",
        "HYBRID",
        "ONSITE",
        "UNKNOWN",
    }

    @staticmethod
    def _normalize_required(value: str) -> str:
        return value.strip()

    @staticmethod
    def _normalize_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

    @classmethod
    def _normalize_work_mode(
        cls,
        value: str | None,
    ) -> str:
        """
        Normalize work mode to a supported value.

        Missing, blank, or unsupported values become UNKNOWN.
        """

        if value is None:
            return "UNKNOWN"

        value = value.strip().upper()

        if not value:
            return "UNKNOWN"

        if value not in cls.ALLOWED_WORK_MODES:
            return "UNKNOWN"

        return value

    def normalize(
        self,
        scraped_job: ScrapedJob,
    ) -> ScrapedJob:
        """
        Normalize a scraped job without changing its meaning.
        """

        return ScrapedJob(
            company=self._normalize_required(
                scraped_job.company,
            ),
            title=self._normalize_required(
                scraped_job.title,
            ),
            location=self._normalize_optional(
                scraped_job.location,
            ),
            url=self._normalize_required(
                scraped_job.url,
            ),
            work_mode=self._normalize_work_mode(
                scraped_job.work_mode,
            ),
            description=self._normalize_optional(
                scraped_job.description,
            ),
            external_job_id=self._normalize_optional(
                scraped_job.external_job_id,
            ),
            salary=self._normalize_optional(
                scraped_job.salary,
            ),
            posted_date=scraped_job.posted_date,
        )