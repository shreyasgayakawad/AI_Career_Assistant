"""
Answer Bank Repository

Repository for AnswerBankEntry database operations.

Every lookup is scoped to a user id so one user can never read or
delete another user's saved answers.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository

from app.models.answer_bank_entry import AnswerBankEntry


class AnswerBankRepository(BaseRepository[AnswerBankEntry]):
    """
    Repository for AnswerBankEntry entities.
    """

    def __init__(self, session: Session):
        super().__init__(AnswerBankEntry, session)

    def get_for_user(self, user_id: int) -> list[AnswerBankEntry]:
        """
        Retrieve all answer bank entries belonging to a user,
        oldest first for stable display order.
        """

        statement = (
            select(AnswerBankEntry)
            .where(AnswerBankEntry.user_id == user_id)
            .order_by(
                AnswerBankEntry.created_at,
                AnswerBankEntry.id,
            )
        )

        return list(self.session.scalars(statement).all())

    def get_by_id_for_user(
        self,
        entry_id: int,
        user_id: int,
    ) -> AnswerBankEntry | None:
        """
        Retrieve a single answer bank entry, but only when it is
        owned by the given user.

        Returns ``None`` when the row does not exist OR belongs to
        another user -- callers cannot distinguish the two cases,
        which is exactly the desired behavior for ownership.
        """

        statement = select(AnswerBankEntry).where(
            AnswerBankEntry.id == entry_id,
            AnswerBankEntry.user_id == user_id,
        )

        return self.session.scalar(statement)


def get_answer_bank_repository(session: Session) -> AnswerBankRepository:
    """
    Factory function to get an AnswerBankRepository instance.
    """

    return AnswerBankRepository(session)
