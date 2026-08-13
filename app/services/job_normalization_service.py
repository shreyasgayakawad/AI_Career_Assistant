"""
Job Normalization Service

Normalizes scraped job data before persistence.
"""

from app.dto.scraped_job import ScrapedJob


class JobNormalizationService:
    """
    Normalizes incoming ScrapedJob objects.
    """

    @staticmethod
    def _normalize_required(value: str) -> str:
        return value.strip()

    @staticmethod
    def _normalize_optional(value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

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
            location=self._normalize_required(
                scraped_job.location,
            ),
            url=self._normalize_required(
                scraped_job.url,
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