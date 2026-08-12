"""
Candidate Profile Schema Migration

Creates the candidate_profiles table when it does not already exist.
"""

from sqlalchemy import inspect, text

from app.database.engine import engine


def migrate() -> None:
    """
    Create the candidate_profiles table when missing.
    """

    inspector = inspect(engine)

    existing_tables = set(
        inspector.get_table_names(),
    )

    if "candidate_profiles" in existing_tables:
        print(
            "Table already exists: candidate_profiles",
        )
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE candidate_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    user_id INTEGER NOT NULL UNIQUE,
                    phone VARCHAR(50),
                    location VARCHAR(255),
                    professional_summary TEXT,
                    skills TEXT,
                    experience TEXT,
                    education TEXT,
                    FOREIGN KEY (user_id)
                        REFERENCES users (id)
                )
                """
            )
        )

    print(
        "Created table: candidate_profiles",
    )


if __name__ == "__main__":
    migrate()
    print(
        "Candidate profile schema migration completed."
    )