# Phase 7 — Resume & Cover Letter Assistance (Zero-Cost)

**Status:** Shipped 2026-08-22 (commits `2b6a08d` predecessor work, `e068ab0`)
This is the archived implementation plan, kept as the template for future
phase plans. Outcome notes are appended at the bottom.

---

## Master rule (applies to every phase)

Nothing gets committed or pushed until it has been reviewed together first:
implement → validate locally → bring the real `git diff`/`git status`/test
output back for review → commit only after that review.

## Hard constraint

No LLM API call, no local LLM server, no paid or free-tier third-party service
anywhere in this phase. "Generate" means fill in a fixed template with real
candidate data — not produce AI-written prose. Reaching for `openai`,
`anthropic`, any AI HTTP API, or a local model runtime is not acceptable
without an explicit team decision first (now codified in ADR 005).

## What this actually is (named honestly)

Not AI-generated resume/cover-letter writing. A deterministic template filled
with real data from `CandidateProfile`, `CandidateWorkExperience`,
`CandidateSkill`, and Phase 5's `JobMatchingService`. The result is explicitly
a draft — labeled as such everywhere — that the user edits and personalizes.
Matches PRODUCT_VISION: "The assistant prepares recommendations. The user
makes the final decision."

## Data availability (verified before planning)

| Needed | Exists? | Notes |
|---|---|---|
| Candidate name | Yes (`User.name`) | |
| Candidate skills | Yes (`CandidateSkill`, Phase 4) | |
| Skills relevant to this job | Yes (`JobMatchingService.calculate_match_score()`) — reuse directly, never recompute | |
| Work history | Yes (`CandidateWorkExperience`) — may be empty; must degrade gracefully | |
| Job title / company | Yes (`JobPosting.title`, `Job.company.name`) | |
| Uploaded résumé file | **No** — `Application.resume_id` is an unconnected bare column; no `Resume` model or upload endpoint. Phase works from structured profile data, not a document | Decision #1 |
| True gap list (job needs vs candidate missing) | **Not reliably buildable** — postings have no structured skills field | Decision #3 |

## Decisions made

1. "Résumé tailoring" = skill-emphasis suggestions from structured profile
   data based on Phase 5 matching — not editing a document that doesn't exist.
   User-facing copy states this explicitly.
2. Cover letter generation = single fixed Python template string filled with
   real data. No LLM, no local model, ever, for this phase.
3. Skill-gap detection out of scope for MVP (would need crude hardcoded
   dictionaries without real NLP).
4. One hardcoded template for MVP — no per-user templates (new schema, bigger
   scope, separate conversation if ever wanted).
5. Drafts are on-demand only — no persistence, no migration. Saved drafts
   would be their own designed feature.

## Tasks (one task = one commit-sized unit)

1. **`ResumeAssistantService`** (`app/services/resume_assistant_service.py`)
   - `get_skill_emphasis(candidate_profile, job_posting)` — thin wrapper over
     `calculate_match_score()` returning its `matched_skills`; empty list on
     the zero-skills case, never a crash.
   - `generate_cover_letter_draft(...)` — fixed template; every bracketed
     section degrades gracefully; output must never contain literal unfilled
     placeholders like `{job_title}`.
2. **API endpoint** — `GET /jobs/{job_posting_id}/cover-letter-draft`,
   authenticated; uses `CandidateProfileService.get_or_create_profile()` (the
   exact bug class that broke Phase 5 twice); 404 for missing postings;
   response includes draft text + skill emphasis + draft note.
3. **Dashboard integration** — "Generate Cover Letter Draft" section in
   `dashboard_job_detail_page()`; draft in editable `<textarea>`; `escape()`
   every piece of candidate-controlled text; reuse Phase 5 matched-skills pill
   styling.
4. **Tests** — `scripts/test_resume_assistant_service.py`: full-data fill,
   placeholder-free check, parity regression against `JobMatchingService`
   (protects "reuse, don't reimplement"), no-work-experience degradation,
   zero-skills case, and TestClient API tests including the brand-new-user
   lazy-profile scenario.

## Validation checklist

- [x] `python -m compileall -q app scripts` clean
- [x] New test script passes with real assertions incl. brand-new-user API scenario
- [x] `python -m scripts.run_all_tests` fully green (49/49)
- [x] `git diff --check` clean
- [x] Manual dashboard walkthrough — draft reads sensibly, no placeholders
- [x] Grep across changed files confirms no `openai`/`anthropic`/AI HTTP calls

## Explicitly out of scope

AI-generated text; skill-gap detection; résumé upload/storage/parsing;
persisted drafts and template customization (Decisions #4–#5).

---

## Outcome notes (appended after delivery)

- All checklist items passed; suite confirmed green twice (implementer and
  independent reviewer run) plus manual walkthrough covering happy path,
  brand-new-user degradation, 404s, JSON endpoint, and XSS escaping of
  candidate-controlled text.
- Incidental finding filed as future ticket: email/password sign-in cannot
  establish the browser session cookie (Google OAuth only).
- Decisions captured in `DECISIONS.md` ADR 005; this plan archived as the
  template for future phases.
