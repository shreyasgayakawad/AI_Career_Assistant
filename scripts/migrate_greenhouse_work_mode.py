"""
Greenhouse Work Mode Refresh

Refreshes work_mode on existing Greenhouse job postings using the
authoritative Greenhouse Location Type metadata.

Existing job postings are matched by Greenhouse source and
external_job_id.
"""

from sqlalchemy import text

from app.connectors.greenhouse_connector import GreenhouseConnector
from app.database.engine import engine
from app.services.job_normalization_service import (
    JobNormalizationService,
)


def migrate() -> None:
    """
    Refresh work_mode values for existing Greenhouse postings.
    """

    print("=" * 60)
    print("Greenhouse Work Mode Refresh")
    print("=" * 60)

    connector = GreenhouseConnector("anthropic")
    normalization_service = JobNormalizationService()

    updated = 0
    unchanged = 0
    skipped = 0

    try:
        data = connector.http_client.get_json(
            connector.api_url,
        )

        jobs = data.get("jobs", [])

        if not isinstance(jobs, list):
            raise RuntimeError(
                "Greenhouse API returned an invalid jobs payload."
            )

        with engine.begin() as connection:
            source_row = connection.execute(
                text(
                    """
                    SELECT id
                    FROM sources
                    WHERE name = :source_name
                    """
                ),
                {
                    "source_name": connector.source_name,
                },
            ).first()

            if source_row is None:
                raise RuntimeError(
                    f"Source '{connector.source_name}' "
                    "does not exist."
                )

            source_id = source_row[0]

            for item in jobs:
                if not isinstance(item, dict):
                    skipped += 1
                    continue

                external_job_id = item.get("id")

                if external_job_id is None:
                    skipped += 1
                    continue

                metadata = item.get("metadata")

                if not isinstance(metadata, list):
                    metadata = None

                raw_work_mode = (
                    connector._extract_work_mode(
                        metadata,
                    )
                )

                normalized_work_mode = (
                    normalization_service._normalize_work_mode(
                        raw_work_mode,
                    )
                )

                result = connection.execute(
                    text(
                        """
                        SELECT work_mode
                        FROM job_postings
                        WHERE source_id = :source_id
                          AND external_job_id = :external_job_id
                        """
                    ),
                    {
                        "source_id": source_id,
                        "external_job_id": str(
                            external_job_id,
                        ),
                    },
                )

                row = result.first()

                if row is None:
                    skipped += 1
                    continue

                current_work_mode = row[0]

                if current_work_mode == normalized_work_mode:
                    unchanged += 1
                    continue

                connection.execute(
                    text(
                        """
                        UPDATE job_postings
                        SET work_mode = :work_mode
                        WHERE source_id = :source_id
                          AND external_job_id = :external_job_id
                        """
                    ),
                    {
                        "work_mode": normalized_work_mode,
                        "source_id": source_id,
                        "external_job_id": str(
                            external_job_id,
                        ),
                    },
                )

                updated += 1

    finally:
        connector.close()

    print()
    print(f"Updated   : {updated}")
    print(f"Unchanged : {unchanged}")
    print(f"Skipped   : {skipped}")
    print()
    print("Greenhouse work mode refresh completed.")


if __name__ == "__main__":
    migrate()