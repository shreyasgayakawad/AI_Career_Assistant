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

### Consequences
- Fast, dependency-free migrations during early, rapidly-changing schema phases.
- Revisit trigger conditions explicitly once either roadmap milestone is reached (see Addendum below).

### Addendum (Phase 2 completion): Trigger Hit, Decision Deferred

**Status:** Deferred to Phase 4

The Phase 2+ roadmap trigger has two conditions, joined by "or":
1. **Multi-source ingestion** — Lever, Ashby, and SmartRecruiters have shipped. **Trigger hit.**
2. **PostgreSQL / multi-user production hosting** — still on SQLite, single local user. **Trigger not hit.**

**Nuance:** adding the three new sources required **zero schema changes**. No new migration script ran, no `ALTER TABLE`, no new column. The existing `Source`/`Job`/`JobPosting` model already handled "multiple sources" generically via `source_id` — that's the design paying off as intended. While the trigger's letter was technically satisfied, the actual justification for Alembic (schema-change complexity getting hard to track by hand) hasn't materialized yet in this codebase.

**Tradeoffs considered:**
- *For adopting now:* setting Alembic up while the schema is simple is easier than retrofitting later; the current manual-script approach is somewhat fragile (no version tracking beyond each script's own inspection check); Alembic is free and open-source (BSD-licensed), no cost concern.
- *For deferring:* introducing Alembic now means an "empty" adoption — `alembic init` and a baseline revision matching current state, but no real migration to actually write yet. The next genuine schema-change trigger is Phase 4 (structured candidate profile — turning free-text skills/experience into real relational tables), a more natural, concrete moment to introduce it alongside an actual meaningful migration rather than a synthetic one.

**Decision:** defer Alembic adoption until Phase 4, when a real schema change naturally exists to pair it with.

**Consequence:** the 6 existing `scripts/migrate_*.py` files remain in place with no version tracking beyond each script's own inspection checks, until Phase 4 introduces Alembic alongside its first real migration.

---

## ADR 004: Test Suite Standardization

### Context
The repository houses modular test suites under `scripts/test_*.py` that test connectors, normalization, repositories, services, and API routes.

### Decision
A standardized test runner is provided via `scripts/run_all_tests.py` (executed as `python -m scripts.run_all_tests` or `.\venv\Scripts\python.exe -m scripts.run_all_tests`), discovering all `test_*.py` modules, running them in isolated sub-processes, timing execution, and reporting a consolidated pass/fail summary.

### Consequences
- Fast regression testing across the entire platform in a single command.
- Direct compatibility with standard CI/CD pipelines.
- Test scripts are subprocess-isolated with `PYTHONIOENCODING=utf-8` forced on the child environment, since non-ASCII job data (e.g. international postings) previously caused `UnicodeEncodeError` failures under Windows' default console codepage.

---

## ADR 005: Deterministic Resume & Cover Letter Assistance (No LLM)

### Context
Phase 7 required "resume tailoring" and cover letter generation. Three constraints shaped the decision: (1) no resume file exists in this system — there is no upload, storage, or parsing feature, only structured profile data; (2) job postings carry no structured skills field, so genuine "you're missing X" gap detection is not reliably buildable without real NLP; (3) any LLM-based approach introduces cost, external dependencies, nondeterministic output, and data-privacy concerns. The product vision states: *"The assistant prepares recommendations. The user makes the final decision."*

### Decision
- **Skill emphasis** is a thin wrapper over `JobMatchingService.calculate_match_score()` (Phase 5): it returns that service's `matched_skills` directly and never reimplements matching. A parity regression test in `scripts/test_resume_assistant_service.py` asserts the two cannot drift apart.
- **Cover letters** are produced by filling one fixed template string with real candidate/job data (`User.name`, `CandidateWorkExperience`, matched skills, `JobPosting.title`, company name). Missing data degrades gracefully — shorter generic letter, never crashes, never literal unfilled placeholders.
- **Drafts are on-demand only**: no persistence, no new tables, no per-user templates for the MVP. Saved drafts or customizable templates would require new schema and their own design conversation.
- **Hard constraint:** no LLM API call, no local model runtime (Ollama, llama.cpp, etc.), no paid or free-tier third-party AI service anywhere in this feature — enforced by a grep check across changed files in the pre-commit validation checklist.
- **Out of scope:** job-description skill-gap detection (would require crude hardcoded dictionaries), resume upload/parsing, draft persistence.

### Consequences
- Zero marginal cost per draft; output is fully deterministic and testable.
- Output quality is bounded by the template; drafts are explicitly labeled as starting points the user must personalize.
- If genuinely generative text is ever wanted, that requires an explicit team decision to overturn the hard constraint above — it is not an implementation detail anyone may swap in unilaterally.