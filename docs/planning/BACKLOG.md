# AI Career Assistant

# BACKLOG

**Status:** Active

Priority Legend

🔴 High Priority
🟡 Medium Priority
🟢 Low Priority

---

# Completed Work

The following capabilities have already been implemented and are no longer active backlog items.

## Core Backend

- [x] Application structure under `app/`
- [x] Repository pattern
- [x] Service layer
- [x] Database initialization
- [x] Database schema migration scripts
- [x] User-specific application tracking
- [x] Candidate profile persistence

## Authentication & Portal Integration

- [x] Google OAuth authentication
- [x] Google login state management
- [x] Google identity linking
- [x] Secure browser session handling
- [x] LinkedIn OAuth flow
- [x] Encrypted portal credential storage
- [x] Portal connection management

## Job Discovery & Application Flow

- [x] Job and company models
- [x] Job posting model
- [x] Job search service
- [x] Job posting search filters
- [x] Career dashboard
- [x] Job detail pages
- [x] Application tracking
- [x] Mark-as-applied workflow
- [x] My Applications page

## Candidate Profile

- [x] Candidate profile model
- [x] Candidate profile repository
- [x] Candidate profile service
- [x] Candidate profile API
- [x] Candidate profile browser page
- [x] Candidate profile update workflow
- [x] Candidate profile database migration
- [x] Candidate profile tests

## Multi-Source Job Discovery

- [x] Lever connector (verified live: 308 postings, palantir board)
- [x] Ashby connector (verified live: 33 postings, linear board)
- [x] SmartRecruiters connector (verified live: 941 postings across pagination, continental board)
- [x] Job normalization enforced for all sources via `JobDiscoveryService`
- [x] Duplicate detection verified across all new connectors (fresh import + no-op re-run)
- [x] Remote-job / work-mode filtering (`REMOTE`/`HYBRID`/`ONSITE`/`UNKNOWN`) across all sources
- [x] Generic `scripts/import_jobs.py` replacing per-source import scripts
- [x] Fixed a `UnicodeEncodeError` in the test runner surfaced by non-English job postings (SmartRecruiters/Continental)

---

# Epic 3 - Core Backend

## Remaining Technical Tasks

- [x] Improve configuration loading
- [x] Improve logging
- [x] Organize database module
- [x] Standardize unit testing framework
- [x] Evaluate database migration framework

---

# Epic 4 - Job Discovery Engine

## Features

* Search jobs from multiple platforms
* Search remote jobs
* Filter by role and location
* Remove duplicate jobs

## Technical Tasks

- [x] Job normalization
- [x] Duplicate detection
- [x] Remote-job filtering
- [x] Company careers scraper — delivered as four connectors (Greenhouse, Lever, Ashby, SmartRecruiters) rather than a single generic scraper, since each ATS platform has its own API shape
- [ ] Advanced search filters — moved to Epic 4 follow-up / Phase 3 scope (see below)

## Deferred / Not Planned

- [ ] **Workday connector** — investigated; requires POST requests with a JSON body and a `tenant`/`site`/`wd_server` triplet instead of a single `company` parameter, unlike the four sources already implemented. Scoped as its own future task, not blocking further work.
- [ ] **Naukri scraper** — deferred until candidate profile and matching are further along.
- [ ] **RemoteOK scraper** — deferred, same reasoning as Naukri.
- [ ] **LinkedIn job scraper** — not planned. No public jobs API exists; scraping would violate LinkedIn's Terms of Service. Would require an official Talent Solutions partnership, which is a business decision outside engineering scope.
- [ ] **Indeed job scraper** — not currently planned; revisit if/when a legitimate public API path is identified.
- [ ] **Wellfound scraper** — not currently planned, same reasoning as Indeed.

---

# Epic 5 - AI Intelligence Engine

## Features

* AI job matching
* Resume optimization
* Cover letter generation
* ATS optimization
* Skill-gap analysis

## Technical Tasks

- [ ] Resume model and document management
- [ ] Resume matching engine
- [ ] Resume tailoring engine
- [ ] Cover letter generator
- [ ] Prompt management
- [ ] AI service layer
- [ ] ATS optimization
- [ ] Skill-gap analysis

---

# Epic 6 - Networking Engine

## Features

* Find recruiters
* Find employees
* Referral assistance
* Outreach tracking

## Technical Tasks

- [ ] LinkedIn employee search
- [ ] Recruiter finder
- [ ] Referral message generator
- [ ] Outreach tracker

---

# Epic 7 - Career Dashboard

## Features

* Application tracking
* Career analytics
* Match scores
* Progress dashboard

## Technical Tasks

- [x] Dashboard UI
- [ ] Analytics service
- [ ] Charts and reports
- [ ] Application timeline
- [ ] Match score display
- [ ] Career progress reports

---

# Future Ideas

These ideas are intentionally out of scope for the current milestones.

- Chrome extension
- Email integration
- Calendar integration
- Salary intelligence
- GitHub profile analysis
- Learning recommendations
- AI interview coach

---

# Definition of Done

A backlog task is complete only when:

- Implementation completed
- Documentation updated when applicable
- Tests added when applicable
- Code reviewed
- Changes committed
- Repository remains clean

---

# Backlog Rules

1. New ideas begin in `FEATURE_IDEAS.md`.
2. Approved work moves into this backlog.
3. A backlog item becomes part of a sprint only after scope is defined.
4. Completed items are marked `[x]`.
5. Avoid duplicating completed work in active backlog sections.
6. Prefer small, verifiable implementation tasks.