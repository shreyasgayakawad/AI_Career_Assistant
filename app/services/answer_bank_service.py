"""
Answer Bank Service

Provides business logic for a user's reusable saved answers
("answer bank") consumed by the Apply Kit on the job-detail page.
"""

from types import SimpleNamespace

from sqlalchemy.orm import Session

from app.models.answer_bank_entry import AnswerBankEntry
from app.repositories.answer_bank_repository import (
    AnswerBankRepository,
)


class AnswerBankService:
    """
    Business service for answer bank entries.
    """

    def __init__(self, session: Session):
        self.repository = AnswerBankRepository(session)

    def list_answers(self, user_id: int) -> list[AnswerBankEntry]:
        """
        List all of a user's saved answers.
        """

        return self.repository.get_for_user(user_id)

    def add_answer(
        self,
        user_id: int,
        *,
        question_text: str,
        answer_text: str,
    ) -> AnswerBankEntry:
        """
        Save a new question/answer pair for the user.

        Raises ``ValueError`` when either field is blank after
        trimming whitespace -- both halves of the pair are required
        for an entry to be useful when copying into an external form.
        """

        cleaned_question = (question_text or "").strip()
        cleaned_answer = (answer_text or "").strip()

        if not cleaned_question:
            raise ValueError("Question text must not be empty.")

        if not cleaned_answer:
            raise ValueError("Answer text must not be empty.")

        entry = AnswerBankEntry(
            user_id=user_id,
            question_text=cleaned_question,
            answer_text=cleaned_answer,
        )

        return self.repository.create(entry)

    def remove_answer(
        self,
        user_id: int,
        entry_id: int,
    ) -> SimpleNamespace | None:
        """
        Remove one of the user's saved answers.

        Returns a snapshot of the removed entry's data, or ``None``
        if it was not found or not owned by this user.

        A snapshot (rather than the ORM object itself) is returned
        because the session's default expire-on-commit behavior makes
        the original object's attributes unreadable immediately after
        the row is deleted and the transaction commits.
        """

        entry = self.repository.get_by_id_for_user(
            entry_id=entry_id,
            user_id=user_id,
        )

        if entry is None:
            return None

        removed_snapshot = SimpleNamespace(
            id=entry.id,
            question_text=entry.question_text,
            answer_text=entry.answer_text,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )

        self.repository.session.delete(entry)
        self.repository.session.commit()

        return removed_snapshot
