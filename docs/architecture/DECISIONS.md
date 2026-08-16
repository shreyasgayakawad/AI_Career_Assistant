# Architecture Decision Records (ADR)

This document records the foundational architecture decisions for the AI Career Assistant platform.

---

## ADR 001: Environment & Secrets Isolation

### Context
To prevent accidental exposure of production or personal OAuth credentials, JWT secrets, and Fernet encryption keys when sharing, demoing, or maintaining the repository, secrets must be isolated from the working tree while remaining seamlessly accessible during local execution.

### Decision
`app/config/settings.py` resolves `.env` configuration using a hierarchical fallback order:
1. `ENV_FILE` environment variable (if explicitly set).
2. Sibling directory: `../AI_Career_Assistant_key/.env` (isolated local secret storage adjacent to workspace).
3. Local workspace `.env` file (gitignored).
4. Standard parent directory traversal via `dotenv.load_dotenv()`.

### Consequences
- Secrets stay strictly outside Git commits and the primary working tree.
- The application boots seamlessly in development without manual shell exports.

---

## ADR 002: Structured Logging Architecture

### Context
The application previously wrote unrotated plain text logs to `logs/job_bot.log`. Unbounded growth risked disk bloat, and runtime log levels could not be altered without code changes.

### Decision
`app/utils/logger.py` uses Python's standard `logging` with:
- `RotatingFileHandler` (5 MB per file, max 3 backup files).
- `StreamHandler` for interactive console stdout.
- Runtime log level configured via the `LOG_LEVEL` environment variable (default: `INFO`).

### Consequences
- Bounded disk usage with log rotation.
- Standardized timestamped, leveled log format across all services and background workers.

---

## ADR 003: Database Migration Framework Evaluation

### Context
During Phase 1 (Foundation & Stabilization), schema migrations are handled using idempotent Python scripts under `scripts/migrate_*.py`. We evaluated transitioning immediately to Alembic versus retaining idempotent migration scripts.

### Options Evaluated
1. **Idempotent Python Migration Scripts (`scripts/migrate_*.py`)**:
   - *Pros:* Simple, zero extra dependencies, idempotent (`IF NOT EXISTS` / inspection checks), explicit, easy to run in standalone PowerShell scripts.
   - *Cons:* Manual tracking of execution order; no automatic rollback graph.
2. **Alembic (SQLAlchemy Migration Framework)**:
   - *Pros:* Auto-generation from ORM diffs, linear revision history, branch merging, downgrade support.
   - *Cons:* Added migration setup overhead during rapid Phase 1 model schema changes.

### Decision
- **Phase 1 (Current):** Retain and maintain the verified idempotent migration scripts under `scripts/migrate_*.py`.
- **Phase 2+ (Roadmap Trigger):** Adopt Alembic when expanding to multi-source ingestion (Phase 2) or migrating from SQLite to PostgreSQL for multi-user production hosting.

---

## ADR 004: Test Suite Standardization

### Context
The repository houses 36 modular test suites under `scripts/test_*.py` that test connectors, normalization, repositories, services, and API routes.

### Decision
A standardized test runner is provided via `scripts/run_all_tests.py` (executed as `python -m scripts.run_all_tests` or `.\venv\Scripts\python.exe -m scripts.run_all_tests`), discovering all `test_*.py` modules, running them in isolated sub-processes, timing execution, and reporting a consolidated pass/fail summary.

### Consequences
- Fast regression testing across the entire platform in a single command (~30s).
- Direct compatibility with standard CI/CD pipelines.
