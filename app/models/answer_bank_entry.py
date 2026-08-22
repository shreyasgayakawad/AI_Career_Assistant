"""
Answer Bank Entry Model

Represents one reusable saved answer ("answer bank" entry) that a
user keeps for common questions asked by external application forms.
"""

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel


class AnswerBankEntry(BaseModel):
    """
    A saved question/answer pair belonging to exactly one user.
    """

    __tablename__ = "answer_bank_entries"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
