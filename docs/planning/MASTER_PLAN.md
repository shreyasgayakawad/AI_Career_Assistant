# AI Career Assistant

# MASTER PLAN

**Status:** Active Development

**Current Version:** v0.1.0

**Repository Status:** Core application development in progress

---

# Project Vision

Build an AI-powered Career Operating System that helps professionals discover jobs, optimize applications, build professional networks, prepare for interviews, and manage their careers from a single intelligent platform.

---

# Completed Work

## Epic 1 — Project Foundation

Completed:

* Project initialized
* Git repository configured
* Python environment configured
* Virtual environment configured
* Dependencies installed
* Documentation structure created
* Initial database prototype
* Product Vision documented
* README created
* System Architecture documented

---

## Epic 2 — Authentication & Portal Integration

Completed:

* Google OAuth authentication
* Google login state management
* Google identity linking
* Secure browser session handling
* LinkedIn OAuth flow
* Encrypted portal credential storage
* Portal connection management

---

## Epic 3 — Core Backend

Completed:

* Application structure under `app/`
* SQLAlchemy database models
* Repository pattern
* Service layer
* Configuration management
* Database initialization
* Database schema migration scripts
* User-specific application tracking
* Candidate profile persistence

---

## Epic 4 — Job Discovery & Application Flow

Completed:

* Job and company models
* Job posting model
* Job search service
* Job posting search filters
* Career dashboard
* Job detail pages
* Application tracking
* Mark-as-applied workflow
* My Applications page

---

## Epic 5 — Candidate Profile

Completed:

* Candidate profile model
* Candidate profile repository
* Candidate profile service
* Candidate profile API
* Candidate profile browser page
* Candidate profile update workflow
* Candidate profile database migration
* Candidate profile tests

---

# Current Milestone

## Phases 5–7 Delivered — Planning Reset

**Status:** Transition point

Core backend, multi-source job discovery, structured candidate profile, deterministic job matching (Phase 5), application status tracking (Phase 6), and template-based resume & cover letter drafting (Phase 7) are shipped, tested, and committed. See `PHASES.md` for the canonical phase list and next-phase candidates.

---

# Current Epic

## Epic 5 — Intelligence Engine (Partially Delivered)

### Objective

Deliver career intelligence without violating the project's Free-of-Cost principle: deterministic matching, template-based drafting, and honest labeling of what is and is not AI.

### Current Status

Matching (Phase 5) and draft assistance (Phase 7) are shipped. ATS optimization and skill-gap analysis remain planned; both need their own design conversations before implementation.

---

# Current Sprint

## Documentation & Planning Synchronization (2026-08-22)

### Goal

Bring planning documentation back in sync with the implemented system after Phases 5–7.

### Current Tasks

* [x] Record Phase 7 decisions in `DECISIONS.md` (ADR 005)
* [x] Update README roadmap statuses
* [x] Create CHANGELOG entries for recent phases
* [x] Add Free-of-Cost principle to `PRODUCT_VISION.md`
* [x] Create canonical `PHASES.md` phase tracker
* [x] Archive the Phase 7 implementation plan under `docs/planning/phases/`
* [ ] Select and scope the next phase (Apply Kit is the leading candidate — see `BACKLOG.md` Future Ideas)

---

# Upcoming Epics

## Epic 4

Job Discovery Engine

Planned capabilities:

* Multi-platform job discovery
* Remote job support
* Job normalization
* Duplicate detection
* Advanced search filters

---

## Epic 5

AI Intelligence Engine

Partially delivered:

* AI job matching — shipped Phase 5 as deterministic, zero-cost keyword-based scoring (no LLM)
* Resume tailoring — shipped Phase 7 as skill-emphasis suggestions from structured profile data
* Cover letter generation — shipped Phase 7 as fixed-template drafts; explicitly no AI text generation (see DECISIONS.md ADR 005)

Still planned:

* ATS optimization
* Skill-gap analysis

---

## Epic 6

Networking Engine

Planned capabilities:

* Recruiter discovery
* Employee discovery
* Referral assistance
* Outreach tracking

---

## Epic 7

Career Dashboard

Planned capabilities:

* Application analytics
* Match scores
* Career insights
* Progress reports

---

## Epic 8

Public Release

Planned capabilities:

* Stable release
* Complete documentation
* Test coverage
* Deployment guide
* Open-source publication

---

# Technical Debt

Current technical debt:

* Browser UI is implemented directly in route modules as server-rendered strings (`web.py`); a templating layer is a candidate future refactor
* Email/password sign-in cannot establish a browser session cookie — only Google OAuth does; email/password users can only drive the app via API/Bearer (see `BACKLOG.md` Future Ideas)
* Database migrations remain script-based; Alembic adoption deferred by ADR 003 addendum until a real schema change lands
* `ROADMAP.md`, `PRODUCT_VISION.md`, and parts of `BACKLOG.md` contain mojibake/escaped-markdown artifacts from earlier encoding mishaps; content is being corrected opportunistically
* `docs/features/`, `docs/meetings/`, and `docs/research/` are empty scaffolding

Resolved since this list was last reviewed: unit testing framework standardized (ADR 004); legacy prototype migration completed; configuration loading consolidated via ADR 001.

---

# Parking Lot

Future ideas:

* Career Profile Engine
* Skill Gap Analysis
* Recruiter CRM
* Salary Intelligence
* Interview Coach
* Chrome Extension
* Email Integration
* Calendar Integration
* GitHub Profile Analysis

---

# Definition of Done

A task is complete only when:

* Implementation completed
* Documentation updated when applicable
* Git repository clean
* Tests added when applicable
* Code reviewed
* Changes committed

---

# Session Workflow

Every development session follows this process:

1. Open `MASTER_PLAN.md`
2. Select one task
3. Complete one task
4. Verify the result
5. Commit the changes
6. Update `MASTER_PLAN.md`

---

# Long-Term Goal

Transform AI Career Assistant into a Career Operating System that assists professionals throughout their entire career journey, from discovering opportunities to continuous professional growth.

# Development Rules

To keep the project consistent, every development session follows these principles:

1. Complete one task at a time.
2. Verify every completed task before moving on.
3. Commit every completed milestone to Git.
4. Update documentation whenever architecture or functionality changes.
5. Prioritize maintainability over speed.
6. Avoid duplicate code and duplicate responsibilities.
7. Keep the repository in a clean, buildable state after every session.
8. Preserve the Free-of-Cost constraint (see `PRODUCT_VISION.md`, Guiding Principles): no feature may introduce paid APIs, subscriptions, metered services, or reliance on free-tier external services — including LLM/AI-service calls, even free ones. Features that cannot meet this constraint are deferred or redesigned, not funded by exceptions.
9. Nothing is committed or pushed until it has been reviewed: implement → validate locally → review the real diff and test output together → commit only after that review.