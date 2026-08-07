"""
Database Seeder

Loads reference data into the database.
"""

import json
from pathlib import Path

# Register all SQLAlchemy models
import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.source import Source
from app.repositories.source_repository import SourceRepository


def seed_sources() -> None:
    """
    Seed the Source table from data/sources.json.
    """

    session = SessionLocal()

    try:
        repository = SourceRepository(session)

        json_path = Path("data/sources.json")

        with json_path.open("r", encoding="utf-8") as file:
            sources = json.load(file)

        existing_sources = {
            source.name
            for source in repository.get_all()
        }

        created = 0

        for source_data in sources:

            if source_data["name"] in existing_sources:
                continue

            repository.create(
                Source(
                    **source_data,
                )
            )

            created += 1

        print(f"Added {created} new sources.")

    finally:
        session.close()


if __name__ == "__main__":
    seed_sources()