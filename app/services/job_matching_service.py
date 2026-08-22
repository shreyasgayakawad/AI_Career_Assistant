"""
Job Matching Service

Provides deterministic, rule-based skill-overlap scoring between
candidate profiles and job postings. Zero-cost: no LLM, no external API.
"""

import re
from dataclasses import dataclass

from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.job_posting import JobPosting


@dataclass
class MatchResult:
    """
    Result of a candidate-vs-job match calculation.

    overall_score is None when the candidate has no skills on their
    profile -- this is deliberately distinct from 0.0, which would
    otherwise be indistinguishable from "we checked and you match
    nothing." Callers must handle the None case explicitly rather
    than accidentally treating an unscored candidate as a 0% match.
    """

    overall_score: float | None
    matched_skills: list[str]
    unmatched_skills: list[str]
    location_match: bool | None
    zero_skills_message: str | None


class JobMatchingService:
    """
    Deterministic, rule-based job matching service.

    Matches candidates to job postings based on skill overlap and
    location compatibility. No ML, no LLM, no external API calls.
    """

    _MIN_SKILL_LENGTH = 3

    def calculate_match_score(
        self,
        candidate_profile: CandidateProfile,
        job_posting: JobPosting,
    ) -> MatchResult:
        """
        Calculate the match score between a candidate profile and a
        job posting.
        """

        candidate_skills = self._get_candidate_skills(candidate_profile)

        if not candidate_skills:
            return MatchResult(
                overall_score=None,
                matched_skills=[],
                unmatched_skills=[],
                location_match=self._check_location_match(
                    candidate_profile.location,
                    job_posting.location,
                ),
                zero_skills_message=(
                    "Add skills to your profile to see match scores."
                ),
            )

        matched_skill_names: list[str] = []
        unmatched_skill_names: list[str] = []

        job_text = (
            job_posting.title
            + " "
            + (job_posting.description or "")
        )

        for skill in candidate_skills:
            skill_name = skill.name

            if len(skill_name) < self._MIN_SKILL_LENGTH:
                unmatched_skill_names.append(skill_name)
                continue

            pattern = r"\b" + re.escape(skill_name) + r"\b"

            if re.search(pattern, job_text, re.IGNORECASE):
                matched_skill_names.append(skill_name)
            else:
                unmatched_skill_names.append(skill_name)

        matched_count = len(matched_skill_names)
        total_count = len(candidate_skills)
        overall_score = (matched_count / total_count) * 100.0

        location_match = self._check_location_match(
            candidate_profile.location,
            job_posting.location,
        )

        return MatchResult(
            overall_score=round(overall_score, 2),
            matched_skills=matched_skill_names,
            unmatched_skills=unmatched_skill_names,
            location_match=location_match,
            zero_skills_message=None,
        )

    @staticmethod
    def _get_candidate_skills(
        candidate_profile: CandidateProfile,
    ) -> list[CandidateSkill]:
        return candidate_profile.skills_list or []

    @staticmethod
    def _check_location_match(
        candidate_location: str | None,
        job_location: str | None,
    ) -> bool | None:
        if not candidate_location or not job_location:
            return None

        candidate_lower = candidate_location.lower()
        job_lower = job_location.lower()

        candidate_in_job = candidate_lower in job_lower
        job_in_candidate = job_lower in candidate_lower

        return candidate_in_job or job_in_candidate