# PHASES

Canonical tracker for the project's phased delivery.

**Governing constraint:** every phase must honor the Free-of-Cost principle
(`PRODUCT_VISION.md`, Guiding Principles) and the review-first workflow
(`MASTER_PLAN.md`, Development Rules 8–9). A phase is complete only when its
features are implemented, documented, tested, reviewed together, and committed.

Per-phase implementation plans live in `docs/planning/phases/`.

---

## Shipped

| Phase | Name | What was delivered | Key docs / evidence |
|---|---|---|---|
| 1 | Stabilization & Core Foundation | Repository/service architecture, config loading (ADR 001), structured logging (ADR 002), test runner (ADR 004) | `MASTER_PLAN.md` Epics 1–3 |
| 2 | Multi-Source Job Discovery | Greenhouse, Lever, Ashby, SmartRecruiters, Workday connectors; normalization & duplicate detection via `JobDiscoveryService`; generic import script | `BACKLOG.md` Multi-Source section |
| 3 | Rich Search Filters | Location, posted-after, salary presence/range parsing, work mode, employment type, experience level, multi-token keyword search | `scripts/test_job_search_*.py` |
| 4 | Structured Candidate Career Profile | Skills, work experience, education with dashboard CRUD and lazy profile creation | `scripts/test_candidate_profile_structured.py` |
| 5 | Job Matching | Deterministic, zero-cost keyword-based match scoring (`JobMatchingService`) with graceful zero-skills case | commit `bd3155b` |
| 6 | Application Status Tracking | Application lifecycle status fields and dashboard flow | commit `865ff22` |
| 7 | Resume & Cover Letter Draft Assistance | Fixed-template cover-letter drafts filled from real profile data + skill-emphasis suggestions reusing Phase 5 matching. Explicitly no AI text generation | `phases/phase-07-resume-assistant.md`, ADR 005, commit `e068ab0` |

---

## Candidates for next phases (unscoped until selected)

Ordering below reflects current team thinking as of 2026-08-22; each becomes a
real phase only after a written plan like Phase 7's is reviewed together first.

| Candidate | One-line intent | Notes |
|---|---|---|
| Apply Kit | Per-job application handoff: deep link (`posting_url` exists on every posting), copy-ready profile block, editable draft letter, reusable answer bank | Directly serves the user goal "apply free of cost" — applying is free everywhere; time-to-apply is the real cost. Answer bank needs a small new table (first persistent user data beyond the profile) |
| Browser session fix | Email/password sign-in currently cannot set the dashboard session cookie; only Google OAuth does | Small standalone auth UX ticket discovered during the Phase 7 walkthrough |
| Résumé file storage | Upload/store the user's own résumé file for one-download access at ATS portals | Larger scope: upload endpoints, size/type limits, storage location. Hook already exists: unconnected `Application.resume_id` column |
| Profile paste-import | Parse pasted LinkedIn-profile text into structured skills/experience with explicit confirm/edit step | User-consented alternative to rejected scraping approaches |

---

## Rejected / not planned (do not re-litigate without new facts)

| Idea | Why rejected | Date |
|---|---|---|
| LLM/AI-generated resumes & cover letters | Violates Free-of-Cost principle; nondeterministic; Truth First requires real data only. Overturning needs explicit team decision (ADR 005) | 2026-08-22 |
| Live career-data pull from LinkedIn | OIDC login provides identity only; work history/skills need restricted scopes or ToS-violating scraping; account-ban risk | 2026-08-22 |
| Live career-data pull from Gmail/Drive wholesale | Restricted OAuth scopes require Google's paid security audit; inbox scanning fails trust test | 2026-08-22 |
| Job-description skill-gap detection | No structured skills field on postings; would require crude hardcoded dictionaries without real NLP (Phase 7 Decision #3) | 2026-08-22 |
