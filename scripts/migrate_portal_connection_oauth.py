"""
Portal Connection OAuth Schema Migration

Adds OAuth-related columns to the existing portal_connections table
without deleting existing portal connection records.
"""

from sqlalchemy import inspect, text

from app.database.engine import engine


def migrate() -> None:
    """
    Add missing OAuth columns to portal_connections.
    """

    inspector = inspect(engine)

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(
            "portal_connections"
        )
    }

    migrations = {
        "external_user_id": (
            "ALTER TABLE portal_connections "
            "ADD COLUMN external_user_id VARCHAR(255)"
        ),
        "oauth_scopes": (
            "ALTER TABLE portal_connections "
            "ADD COLUMN oauth_scopes VARCHAR(1000)"
        ),
        "token_expires_at": (
            "ALTER TABLE portal_connections "
            "ADD COLUMN token_expires_at DATETIME"
        ),
    }

    with engine.begin() as connection:
        for column_name, statement in migrations.items():
            if column_name not in existing_columns:
                connection.execute(text(statement))
                print(
                    f"Added column: {column_name}"
                )
            else:
                print(
                    f"Column already exists: {column_name}"
                )


if __name__ == "__main__":
    migrate()
    print(
        "Portal connection OAuth schema migration completed."
    )