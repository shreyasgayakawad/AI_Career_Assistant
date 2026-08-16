# AI Career Assistant — Coding Standards & Development Guidelines

This document establishes the official coding standards and engineering workflows for the AI Career Assistant repository.

---

## 1. Architectural Boundaries

- **Separation of Concerns:**
  - `BaseConnector` / Connectors: Fetch raw external job data and output `ScrapedJob` DTOs only.
  - `JobNormalizationService`: Normalize location strings, titles, and classify `work_mode`.
  - `JobImportService` / `JobDiscoveryService`: Coordinate import, deduplication, and persistence.
  - Repositories: Direct SQLAlchemy database queries and persistence only. No business logic.
  - Services: Encapsulate all business rules, authorization checks, and data validation.
  - API Routes: Handle HTTP transport, request validation, authentication dependencies, and route responses.
- **DTOs over Raw Models:** Downstream components depend on standardized DTOs (e.g. `ScrapedJob`), not scraper-specific schemas.
- **Never Put Business Logic in API Routes or Connectors.**

---

## 2. Python & Code Style

- **Python Version:** Python 3.11+ (running on Windows PowerShell environment).
- **Type Annotations:** Use Python standard type hints (`str | None`, `list[T]`, `dict[str, Any]`, `Mapped[T]`) across all services, repositories, and API endpoints.
- **Docstrings & Comments:** Every module, class, and public function must include descriptive docstrings and section headers.
- **SQLAlchemy 2.0 Syntax:** Use 2.0-style statements (`select(...)`, `session.scalars(...)`) and Declarative Mapped types (`Mapped[T] = mapped_column(...)`).

---

## 3. Security & Secrets Management

- **Isolated Credentials:** Real secrets (`JWT_SECRET_KEY`, `CREDENTIAL_ENCRYPTION_KEY`, OAuth secrets) must never be stored in Git.
- **Local Isolation:** Secrets are stored in `../AI_Career_Assistant_key/.env` or local `.env` and resolved by `app/config/settings.py`.
- **Masking:** Secrets must never be logged, printed to console, or passed in error messages.
- **Token Storage:** Sensitive portal access tokens are encrypted at rest using Fernet cryptography.

---

## 4. Testing & Validation

- **Module-Level Execution:** Run tests using the module syntax `python -m scripts.<test_name>` from the project root.
- **Full Suite Runner:** Run `python -m scripts.run_all_tests` before submitting changes.
- **Pre-Commit Checks:**
  ```powershell
  python -m compileall -q app scripts
  python -m scripts.run_all_tests
  git diff --check
  ```

---

## 5. Git & Commit Guidelines

- **Meaningful Commits:** Use clear, descriptive, imperative-mood commit messages (e.g., `Add rotating file handler to logger` instead of `fix logging`).
- **Clean Working Tree:** Keep the working tree clean after completing tasks.
