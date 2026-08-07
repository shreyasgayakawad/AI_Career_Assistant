"""
Test Company Repository

Simple integration script for the CompanyRepository.
"""

# Import all models so SQLAlchemy registers every mapper.
import app.models  # noqa: F401

from app.database.session import SessionLocal
from app.models.company import Company
from app.repositories.company_repository import CompanyRepository


def main() -> None:
    """
    Test creating and retrieving a company.
    """

    session = SessionLocal()

    try:
        repository = CompanyRepository(session)

        company = repository.get_by_name("Google")

        if company is None:
            company = Company(
                name="Google",
                website="https://google.com",
                careers_url="https://careers.google.com",
            )

            company = repository.create(company)
            print(f"Created Company ID: {company.id}")
        else:
            print(f"Company already exists. ID: {company.id}")

        loaded_company = repository.get_by_id(company.id)

        if loaded_company:
            print(f"Retrieved Company: {loaded_company.name}")
        else:
            print("Company not found.")

    finally:
        session.close()


if __name__ == "__main__":
    main()