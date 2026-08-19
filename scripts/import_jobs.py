"""
Import Jobs

Generic job import script that works with any registered connector.

Fetches jobs from the specified scraper via JobDiscoveryService, which
normalizes them (JobNormalizationService) before persisting them
(JobImportService) — unlike a connector-specific script that calls the
import service directly, this guarantees normalization always runs.

Usage:
    python -m scripts.import_jobs --scraper lever_scraper --source Lever --company palantir
    python -m scripts.import_jobs --scraper ashby_scraper --source Ashby --company linear
    python -m scripts.import_jobs --scraper smartrecruiters_scraper --source SmartRecruiters --company continental
    python -m scripts.import_jobs --scraper greenhouse_scraper --source Greenhouse --company anthropic

Note: the target Source (e.g. "Lever") must already exist in the
sources table. Run `python -m scripts.seed_database` first if it
does not.
"""

import argparse

# Register all SQLAlchemy models.
import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.services.job_discovery_service import JobDiscoveryService


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the import run.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Import jobs from a registered connector into the database."
        ),
    )

    parser.add_argument(
        "--scraper",
        required=True,
        help="Registry key for the connector, e.g. 'lever_scraper'.",
    )

    parser.add_argument(
        "--source",
        required=True,
        help="Source name as stored in the sources table, e.g. 'Lever'.",
    )

    parser.add_argument(
        "--company",
        required=True,
        help=(
            "Company/board identifier passed to the connector, "
            "e.g. 'palantir'. "
            "Required for backward compatibility with existing connectors "
            "that accept a single company argument."
        ),
    )

    parser.add_argument(
        "--kwarg",
        action="append",
        default=[],
        help=(
            "Connector-specific key=value argument (repeatable). "
            "e.g. '--kwarg wd_server=wd1 --kwarg tenant=acme --kwarg site=External'. "
            "Values are collected into a dict passed to the connector via "
            "connector_kwargs. Mutually exclusive with --company for new connectors, "
            "but kept for backward compatibility."
        ),
    )

    return parser.parse_args()


def _build_connector_kwargs(args: argparse.Namespace) -> dict[str, object]:
    """
    Build a connector kwargs dict from parsed CLI arguments.

    Collects --kwarg key=value pairs into a dict. Falls back to --company
    for backward compatibility with existing connectors.
    """

    kwargs: dict[str, object] = {}

    if args.kwarg:
        for kwarg in args.kwarg:
            if "=" not in kwarg:
                raise ValueError(
                    f"Invalid --kwarg format: '{kwarg}'. Expected key=value."
                )
            key, _, value = kwarg.partition("=")
            kwargs[key.strip()] = value.strip()
    else:
        kwargs["company"] = args.company

    return kwargs


def main() -> None:
    """
    Discover, normalize, and import jobs from the specified connector.
    """

    args = parse_args()

    session = SessionLocal()

    try:
        service = JobDiscoveryService(session)

        imported, skipped = service.discover(
            scraper_name=args.scraper,
            source_name=args.source,
            connector_kwargs=_build_connector_kwargs(args),
        )

        print("=" * 50)
        print("Job Import")
        print("=" * 50)
        print(f"Scraper       : {args.scraper}")
        print(f"Source        : {args.source}")
        print(f"Company/Board : {args.company}")
        print()
        print(f"Imported      : {imported}")
        print(f"Skipped       : {skipped}")

    finally:
        session.close()


if __name__ == "__main__":
    main()