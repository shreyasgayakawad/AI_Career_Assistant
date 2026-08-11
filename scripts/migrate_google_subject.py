"""
Google Subject Schema Migration

Adds the Google subject column and unique index to the existing
users table without modifying existing user records.
"""

from sqlalchemy import inspect, text

from app.database.engine import engine


def migrate() -> None:
    """
    Add the Google subject column and unique index when missing.
    """

    inspector = inspect(engine)

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    with engine.begin() as connection:
        if "google_subject" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN google_subject VARCHAR(255)"
                )
            )
            print("Added column: google_subject")
        else:
            print("Column already exists: google_subject")

        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "ix_users_google_subject "
                "ON users (google_subject)"
            )
        )
        print("Unique index verified: ix_users_google_subject")


if __name__ == "__main__":
    migrate()
    print(
        "Google subject schema migration completed."
    )