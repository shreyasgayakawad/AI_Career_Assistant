"""
Resume Assistant Service

Deterministic, template-based draft assistance for cover letters,
built on the candidate's structured profile data and Phase 5's
JobMatchingService.

Zero-cost by design: no LLM, no local model runtime, and no external
API calls of any kind. "Generate" here means fill in a fixed template
with real candidate data -- nothing more. The result is explicitly a
draft: a starting point the user edits and personalizes themselves,
not a finished document.
"""

from datetime import date

from app.models.candidate_profile import CandidateProfile
from app.models.candidate_work_experience import CandidateWorkExperience
from app.models.job_posting import JobPosting
from app.services.job_matching_service import JobMatchingService


COVER_LETTER_DRAFT_NOTE = (
    "Draft assembled automatically from your profile using a fixed "
    "template. It is a starting point to edit and personalize, "
    "not a finished letter."
)


class ResumeAssistantService:
    """
    Template-based resume/cover-letter assistance service.

    All skill matching is delegated to JobMatchingService so there is
    exactly one implementation of that logic in the codebase.
    """

    def __init__(self):
        self.matching_service = JobMatchingService()

    def get_skill_emphasis(
        self,
        candidate_profile: CandidateProfile,
        job_posting: JobPosting,
    ) -> list[str]:
        """
        Return the candidate's skills relevant to this posting.

        A thin wrapper over JobMatchingService.calculate_match_score():
        this deliberately does not reimplement skill matching, so the
        two cannot silently drift apart. An unscored candidate (no
        profile skills) yields an empty list, never an error.
        """

        match_result = self.matching_service.calculate_match_score(
            candidate_profile=candidate_profile,
            job_posting=job_posting,
        )

        if match_result.overall_score is None:
            return []

        return match_result.matched_skills

    def generate_cover_letter_draft(
        self,
        candidate_name: str,
        candidate_profile: CandidateProfile,
        job_posting: JobPosting,
        company_name: str,
    ) -> str:
        """
        Fill a fixed template with real candidate and job data.

        Every optional section degrades gracefully when the underlying
        data does not exist: a candidate with no work experience or no
        matched skills still receives a short, valid letter -- never a
        crash and never literal unfilled placeholders such as
        "{job_title}" in the output.
        """

        skill_emphasis = self.get_skill_emphasis(
            candidate_profile=candidate_profile,
            job_posting=job_posting,
        )

        experience = self._get_most_recent_work_experience(
            candidate_profile,
        )

        safe_job_title = (job_posting.title or "").strip()
        safe_company_name = (company_name or "").strip() or "your organization"

        lines: list[str] = [
            "Dear Hiring Team,",
            "",
            (
                "I am writing to express my interest in the "
                f"{safe_job_title} position at {safe_company_name}."
            ),
        ]

        if experience is not None:
            lines.append("")
            lines.append(self._experience_paragraph(experience))

        if skill_emphasis:
            lines.append("")
            lines.append(
                "In particular, my experience with "
                + self._join_skill_names(skill_emphasis)
                + " aligns well with what you're looking for."
            )

        lines.append("")
        lines.append(
            "I would welcome the opportunity to discuss how my "
            "background could contribute to your team."
        )
        lines.append("")
        lines.append("Sincerely,")

        trimmed_name = (candidate_name or "").strip()

        if trimmed_name:
            lines.append(trimmed_name)

        return "\n".join(lines)

    # --- internal helpers ---------------------------------------------

    @staticmethod
    def _get_most_recent_work_experience(
        candidate_profile: CandidateProfile | None,
    ) -> CandidateWorkExperience | None:
        """
        Pick the most recent work experience entry by start date.

        Entries without a company name are ignored; entries without a
        start date sort as oldest rather than crashing the comparison.
        """

        if candidate_profile is None:
            return None

        experiences = [
            entry
            for entry in (candidate_profile.work_experiences or [])
            if entry.company_name
        ]

        if not experiences:
            return None

        return max(
            experiences,
            key=lambda entry: entry.start_date or date.min,
        )

    @staticmethod
    def _experience_paragraph(
        experience: CandidateWorkExperience,
    ) -> str:
        company = experience.company_name.strip()

        title = (experience.job_title or "").strip()

        if title:
            role_phrase = f"role as {title} at {company}"
        else:
            role_phrase = f"role at {company}"

        return (
            f"In my most recent {role_phrase}, I gained experience "
            "that I believe is directly relevant to this opportunity."
        )

    @staticmethod
    def _join_skill_names(skill_names: list[str]) -> str:
        cleaned = [name.strip() for name in skill_names if name.strip()]

        if not cleaned:
            return ""

        if len(cleaned) == 1:
            return cleaned[0]

        return ", ".join(cleaned[:-1]) + " and " + cleaned[-1]
