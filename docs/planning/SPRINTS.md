# AI Career Assistant

# SPRINTS

**Status:** Active Development

---

# Sprint 3.1 — Planning Synchronization & Core Backend Stabilization

**Status:** Completed

**Epic:** Epic 3 — Core Backend & Application Foundation

## Goal

Synchronize planning documents with the implemented system and complete remaining stabilization tasks (configuration loading, structured logging, database module organization, test runner standardization, and architecture decision records).

## Completed Tasks

- [x] Synchronize `MASTER_PLAN.md` with the implemented system
- [x] Synchronize `BACKLOG.md` with completed and remaining work
- [x] Verify repository and service architecture
- [x] Verify existing application and candidate profile functionality
- [x] Verify existing test scripts
- [x] Verify repository working tree and Git history
- [x] Review and update `DOMAIN_MODEL.md`
- [x] Define architecture decisions in `DECISIONS.md`
- [x] Define coding standards in `CODING_STANDARDS.md`
- [x] Implement external `.env` resolution in `app/config/settings.py`
- [x] Create project `README.md`
- [x] Add rotating file handler and structured logging to `app/utils/logger.py`
- [x] Organize `app/database/__init__.py`
- [x] Create standardized test runner `scripts/run_all_tests.py`

---

# Sprint 3.2 — Job Discovery Expansion

**Status:** Completed

**Epic:** Epic 4 — Job Discovery Engine

## Goal

Expand job discovery beyond the currently implemented job search and posting workflow.

## Completed Tasks

- [x] Define job source connector interface (`BaseConnector`, already in place; new sources registered via `app/connectors/registry.py`)
- [x] Implement source-specific job discovery — added Lever, Ashby, and SmartRecruiters connectors alongside the existing Greenhouse connector
- [x] Normalize discovered jobs — all connectors now route through `JobNormalizationService` via `JobDiscoveryService`; retired a per-source import script (`scripts/import_greenhouse_jobs.py`) that had bypassed normalization entirely
- [x] Detect duplicate jobs — verified for all three new connectors via a fresh import followed by an immediate no-op re-run (posting URL + source/external-ID dedup confirmed working)
- [x] Add remote-job filtering — `work_mode` filtering (`REMOTE`/`HYBRID`/`ONSITE`/`UNKNOWN`) now applies consistently across all four connected sources
- [x] Added a single generic `scripts/import_jobs.py` (`--scraper`, `--source`, `--company`) replacing per-source import scripts

## Deferred (explicitly out of scope for this sprint)

- [ ] **Workday** — investigated; API is meaningfully more complex than the other sources (POST-based with a JSON body, no fixed datacenter number across tenants, requires `tenant`/`site`/`wd_server` instead of a single `company` parameter). Revisit as its own scoped task.
- [ ] **Naukri, RemoteOK** — deferred until the core app (candidate profile, matching) is further along, per product decision.
- [ ] **LinkedIn, Wellfound** — no public jobs API exists for either; LinkedIn access would require an official Talent Solutions partnership (a business decision, not an engineering one) rather than scraping, which would violate their Terms of Service. Not currently planned.
- [ ] **Improve advanced search filters** (salary, employment type, experience level, posted date, skills) — moved to Phase 3 scope; not part of this sprint.

---

# Sprint 3.3 — AI Career Intelligence

**Status:** Planned

**Epic:** Epic 5 — AI Intelligence Engine

## Goal

Introduce AI-powered capabilities using the candidate profile, jobs, and applications already present in the system.

## Candidate Tasks

- [ ] Define AI service boundary
- [ ] Define prompt management strategy
- [ ] Design job-to-candidate matching
- [ ] Design resume management
- [ ] Design resume tailoring
- [ ] Design cover letter generation
- [ ] Design skill-gap analysis

---

# Sprint 3.4 — Networking

**Status:** Planned

**Epic:** Epic 6 — Networking Engine

## Goal

Build the foundations for recruiter discovery, employee discovery, referrals, and outreach tracking.

## Candidate Tasks

- [ ] Define recruiter entity
- [ ] Define employee entity
- [ ] Define referral entity
- [ ] Design recruiter discovery workflow
- [ ] Design employee discovery workflow
- [ ] Design referral workflow
- [ ] Design outreach tracking

---

# Sprint 3.5 — Career Analytics

**Status:** Planned

**Epic:** Epic 7 — Career Dashboard

## Goal

Extend the existing dashboard with meaningful career-search analytics.

## Candidate Tasks

- [ ] Define application lifecycle analytics
- [ ] Design application timeline
- [ ] Design match score presentation
- [ ] Design career progress metrics
- [ ] Design charts and reports

---

# Sprint Rules

1. Work on one sprint task at a time.
2. Verify every completed task before moving to the next task.
3. Keep implementation changes small and reviewable.
4. Add tests when functionality requires them.
5. Update documentation when architecture or behavior changes.
6. Commit completed tasks to Git.
7. Keep the working tree clean at the end of a completed task.
8. Do not implement future sprint work before its scope is defined.

---

# Definition of Done

A sprint task is complete when:

- Implementation is complete when applicable.
- Tests pass when applicable.
- Documentation is updated when applicable.
- Code has been reviewed.
- Git changes are committed.
- The repository is left in a clean state.