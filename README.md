# AI Career Assistant

AI Career Assistant is an intelligent personal job-search and career-management platform. It discovers relevant job opportunities across multiple sources, normalizes and deduplicates listings, tracks applications, matches positions against a candidate's profile, and provides AI-driven career assistance.

---

## 1. Core Architecture & Concepts

The project is built foundation-first with a clean separation of concerns:

```
External Job Boards (Greenhouse, etc.)
        │
        ▼
   Connectors            (BaseConnector → GreenhouseConnector, etc.)
        │
        ▼
 ScrapedJob DTO           (app/dto/scraped_job.py)
        │
        ▼
Normalization Service     (JobNormalizationService)
        │
        ▼
 Import / Discovery       (JobImportService, JobDiscoveryService)
        │
        ▼
 Repositories             (SQLAlchemy, one per entity)
        │
        ▼
   SQL Database           (SQLite / relational database)
        │
        ▼
 Business Services        (Application, CandidateProfile, etc.)
        │
        ▼
      FastAPI             (app/api/routes/)
        │
        ▼
 Browser UI & AI Services
```

### Key Pillars

1. **`ScrapedJob` DTO** (`app/dto/scraped_job.py`): The standard unified data transfer object produced by every connector. Downstream services do not depend on source-specific data formats.
2. **Connectors** (`app/connectors/`): Dedicated classes responsible only for fetching raw job data and converting it into `ScrapedJob` instances.
3. **Normalization** (`app/services/job_normalization_service.py`): Cleans and normalizes locations, titles, descriptions, and classifies `work_mode` (`REMOTE`, `HYBRID`, `ONSITE`, `UNKNOWN`).
4. **Repositories vs. Services**: Repositories handle database persistence only. Business logic resides strictly within Services.
5. **FastAPI Layer** (`app/api/`): Exposes REST API endpoints and server-rendered dashboard templates.

### Domain Model

```
Company ───> Job ───> JobPosting
                          │
                          └─── Application (User + JobPosting)
```

- **Job**: The logical job position (e.g. "Software Engineer").
- **JobPosting**: A specific advertisement for that Job from a specific source.
- **Application**: A user's application record for a specific `JobPosting`, preventing duplicate applications and filtering available search results.

---

## 2. Prerequisites & Setup

### Requirements
- **Python 3.11+** (Windows PowerShell environment)
- **Virtual Environment** (`venv`)

### Installation

Clone the repository and set up the virtual environment:

```powershell
# Clone the repository
git clone https://github.com/shreyasgayakawad/AI_Career_Assistant.git
cd AI_Career_Assistant

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## 3. Environment Configuration

For security and credential isolation, the application supports storing `.env` either inside an external sibling directory or at the project root.

### Resolution Priority

The configuration loader (`app/config/settings.py`) searches for environment variables in the following order:
1. File path specified by the `ENV_FILE` environment variable.
2. Sibling directory: `../AI_Career_Assistant_key/.env` (isolated local secret storage).
3. Project root: `.env`.
4. Default parent directory traversal.

### Sample Environment Variables

Create your `.env` file (e.g., in `../AI_Career_Assistant_key/.env` or `.env`):

```ini
# JWT Authentication
JWT_SECRET_KEY=your_secure_jwt_secret_key_here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Credential Encryption
CREDENTIAL_ENCRYPTION_KEY=your_fernet_credential_encryption_key_here

# OAuth Providers (optional for local dev)
GOOGLE_ENABLED=false
LINKEDIN_ENABLED=false

# Session Cookies
AUTH_COOKIE_NAME=career_access_token
AUTH_COOKIE_SECURE=false

# Logging (optional: DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

> **Security Note:** Never commit `.env` files or credentials to Git.

---

## 4. Database Initialization & Migrations

Initialize the SQLite database and run migration scripts:

```powershell
# Initialize base database tables
python -m app.database.init_db

# Run schema migrations (idempotent)
python -m scripts.migrate_google_subject
python -m scripts.migrate_google_login_state
python -m scripts.migrate_portal_connection_oauth
python -m scripts.migrate_candidate_profile
python -m scripts.migrate_job_posting_work_mode
python -m scripts.migrate_job_posting_work_mode_backfill
```

---

## 5. Running the Application

Start the FastAPI local development server:

```powershell
uvicorn app.main:app --reload
```

The application will be accessible at:
- **Web UI & Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 6. Running Tests & Validation

Run the test suite before submitting any changes:

```powershell
# Run all tests via the test runner
python -m scripts.run_all_tests

# Or run individual test suites
python -m scripts.test_job_posting_work_mode_backfill
python -m scripts.test_candidate_profile
python -m scripts.test_available_jobs_api

# Code compilation check
python -m compileall -q app scripts

# Git diff check
git diff --check
```

---

## 7. Team Workflow & Contribution Rules

1. **PowerShell First:** Use Windows PowerShell syntax for all commands.
2. **One File / One Task:** Keep edits focused, clean, and isolated per task.
3. **Full File Outputs:** Provide full file implementations rather than partial diffs.
4. **Pre-Commit Validation:** Always run `compileall` and test suites before committing.
5. **No Secrets in Git:** Never log, print, or commit sensitive credentials.

---

## 8. Project Roadmap

- **Phase 1: Stabilization & Core Foundation** (In Progress)
- **Phase 2: Multi-Source Job Discovery** (Lever, Ashby, Wellfound, Workday, LinkedIn)
- **Phase 3: Rich Search Filters & Ingestion Pipeline**
- **Phase 4: Structured Candidate Career Profile**
- **Phase 5: AI Job Matching & Gap Analysis**
- **Phase 6: Application Pipeline Lifecycle Tracking**
- **Phase 7: AI Resume & Cover Letter Generation**
- **Phase 8: Autonomous Assistant Career Workflow**
