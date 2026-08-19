"""Backfill salary_min and salary_max columns from existing salary text.

This script reads existing JobPosting.salary text, parses it via the
salary_parser, and populates the new salary_min/salary_max columns.

Usage:
    python -m scripts.migrate_job_posting_salary

Note: Since the current database has no salary text populated, this will
leave salary_min/salary_max as NULL for all rows. The parser will be
activated when new jobs are imported going forward (Task E).
"""

import sys
sys.path.insert(0, "C:\\Users\\Asus\\Documents\\AI_Career_Assistant")

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.job_posting import JobPosting
from app.services.salary_parser import parse_salary_text, format_salary_range


def main() -> None:
    """Backfill salary_min and salary_max from existing salary text."""
    engine = create_engine("sqlite:///./database/jobs.db")
    session = SessionLocal(bind=engine)

    try:
        postings = session.query(JobPosting).all()
        print(f"Total JobPostings: {len(postings)}")

        updated = 0
        for posting in postings:
            if posting.salary:
                min_val, max_val = parse_salary_text(posting.salary)
                posting.salary_min = min_val
                posting.salary_max = max_val
                updated += 1
            else:
                posting.salary_min = None
                posting.salary_max = None

        session.commit()
        print(f"Updated {updated} postings with parsed salary data.")
        print("All other postings have salary_min/salary_max set to None.")

        # Print summary
        with_min = sum(1 for p in postings if p.salary_min is not None)
        with_max = sum(1 for p in postings if p.salary_max is not None)
        print(f"Postings with salary_min set: {with_min}/{len(postings)}")
        print(f"Postings with salary_max set: {with_max}/{len(postings)}")

    finally:
        session.close()


if __name__ == "__main__":
    main()