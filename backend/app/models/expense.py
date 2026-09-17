from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    group_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("groups.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="Other")
    payer_id: Mapped[str] = mapped_column(String(36), ForeignKey("participants.id"), nullable=False)
    subtotal_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    tax_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tip_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fees_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    discounts_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="CAD")
    split_method: Mapped[str] = mapped_column(String(30), nullable=False, default="equal")
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    group: Mapped["Group"] = relationship(back_populates="expenses")
    payer: Mapped["Participant"] = relationship()
    participants: Mapped[list["ExpenseParticipant"]] = relationship(
        back_populates="expense",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ExpenseParticipant(Base):
    __tablename__ = "expense_participants"
    __table_args__ = (UniqueConstraint("expense_id", "participant_id", name="uq_expense_participant"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    expense_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("expenses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    participant_id: Mapped[str] = mapped_column(String(36), ForeignKey("participants.id"), nullable=False)
    share_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    expense: Mapped["Expense"] = relationship(back_populates="participants")
    participant: Mapped["Participant"] = relationship()


from app.models.group import Group, Participant  # noqa: E402
