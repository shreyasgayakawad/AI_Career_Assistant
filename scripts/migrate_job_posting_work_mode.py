"""
Job Posting Work Mode Schema Migration

Adds the work_mode column to the existing job_postings table
without deleting or modifying existing job postings.
"""

from sqlalchemy import inspect, text

from app.database.engine import engine


def migrate() -> None:
    """
    Add the work_mode column to job_postings when missing.

    Existing postings receive UNKNOWN as their initial value.
    """

    inspector = inspect(engine)

    existing_tables = set(
        inspector.get_table_names(),
    )

    if "job_postings" not in existing_tables:
        raise RuntimeError(
            "Table 'job_postings' does not exist."
        )

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(
            "job_postings",
        )
    }

    if "work_mode" in existing_columns:
        print(
            "Column already exists: job_postings.work_mode"
        )
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                ALTER TABLE job_postings
                ADD COLUMN work_mode VARCHAR(20)
                NOT NULL DEFAULT 'UNKNOWN'
                """
            )
        )

    print(
        "Added column: job_postings.work_mode"
    )


if __name__ == "__main__":
    migrate()
    print(
        "Job posting work mode schema migration completed."
    )