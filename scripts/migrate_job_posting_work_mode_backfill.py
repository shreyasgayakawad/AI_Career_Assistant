"""
Job Posting Work Mode Data Backfill

Classifies existing job postings using explicit work-mode
terminology found in the location field.

Rules:
- REMOTE when the location explicitly indicates remote work.
- HYBRID when the location explicitly indicates hybrid work.
- ONSITE when the location explicitly indicates onsite work.
- UNKNOWN when the location does not provide explicit evidence.

The description is intentionally NOT used for classification.
"""

from sqlalchemy import text

from app.database.engine import engine
from app.services.work_mode_classifier import classify_work_mode


def migrate() -> None:
    """
    Backfill existing job postings from UNKNOWN.

    Only UNKNOWN rows are modified.
    """

    with engine.begin() as connection:
        rows = connection.execute(
            text(
                """
                SELECT
                    id,
                    location,
                    work_mode
                FROM job_postings
                WHERE work_mode = 'UNKNOWN'
                ORDER BY id
                """
            )
        ).mappings().all()

        counts = {
            "REMOTE": 0,
            "HYBRID": 0,
            "ONSITE": 0,
            "UNKNOWN": 0,
        }

        for row in rows:
            work_mode = classify_work_mode(
                location=row["location"],
            )

            counts[work_mode] += 1

            if work_mode == "UNKNOWN":
                continue

            connection.execute(
                text(
                    """
                    UPDATE job_postings
                    SET work_mode = :work_mode
                    WHERE id = :posting_id
                    AND work_mode = 'UNKNOWN'
                    """
                ),
                {
                    "work_mode": work_mode,
                    "posting_id": row["id"],
                },
            )

    print("=" * 60)
    print("Job Posting Work Mode Backfill")
    print("=" * 60)
    print(f"REMOTE  : {counts['REMOTE']}")
    print(f"HYBRID  : {counts['HYBRID']}")
    print(f"ONSITE  : {counts['ONSITE']}")
    print(f"UNKNOWN : {counts['UNKNOWN']}")
    print(f"TOTAL   : {len(rows)}")


if __name__ == "__main__":
    migrate()
    print(
        "Job posting work mode backfill completed."
    )