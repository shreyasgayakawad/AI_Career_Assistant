# Changelog

All notable changes to this project are documented here.
Format loosely follows Keep a Changelog. Entries are newest first; dates are YYYY-MM-DD.

---

## 2026-08-22

### Added

- **Template-based resume & cover letter assistance (Phase 7)** (`e068ab0`)
  - New `ResumeAssistantService` (`app/services/resume_assistant_service.py`) providing:
    - `get_skill_emphasis()` — a thin wrapper over Phase 5's `JobMatchingService.calculate_match_score()` that returns its `matched_skills` directly, so skill matching has exactly one implementation in the codebase. Returns an empty list for zero-skill profiles rather than an error.
    - `generate_cover_letter_draft()` — deterministic fill-in of one fixed template using real candidate/job data (`User`, `CandidateProfile`, `CandidateWorkExperience`). Every optional section degrades gracefully: no work experience or no matched skills still yields a short, valid letter with no unfilled placeholders and no crashes.
  - New authenticated endpoint `GET /jobs/{job_posting_id}/cover-letter-draft` returning draft text, the skill-emphasis list, and a fixed note making clear the draft is a starting point to edit, not a finished letter. Uses lazy profile creation (`CandidateProfileService.get_or_create_profile()`), so first-time users get a valid response instead of a crash.
  - Dashboard job-detail page: new "Cover Letter Draft" section rendering the draft inside an editable `<textarea>` plus skill pills reusing the existing matched-skills styling. All candidate-controlled text is HTML-escaped before it reaches the page.
  - Test suite `scripts/test_resume_assistant_service.py` (9 checks) covering template fill, placeholder-free output, parity with `JobMatchingService`, graceful degradation (no work experience / zero skills), and API behaviour including lazy profile creation for brand-new users.
  - **Explicitly not AI-generated:** deterministic template fill of real candidate data only. No LLM calls, no local model runtime, and no third-party AI service calls anywhere in the feature — see ADR 005 in `docs/architecture/DECISIONS.md`.

- **Multi-token keyword search** (`2b6a08d`)
  - Job posting keyword search now splits on whitespace; every token must appear (case-insensitively) in the posting's title or description, with tokens allowed to match different fields in any order ("cloud support" finds "Support Engineer - Cloud Platform").
  - Removed a duplicated legacy query-building block left behind by an earlier edit in `JobPostingRepository.search()`.
  - Test suite `scripts/test_job_search_multi_keyword.py` (8 checks).

### Notes on earlier releases

Phases 1–6 predate the introduction of this changelog; see `git log --oneline`
for their commit history (structured candidate career profile, zero-cost
deterministic job matching, application status tracking, multi-source
connectors, salary/location/work-mode filters).
