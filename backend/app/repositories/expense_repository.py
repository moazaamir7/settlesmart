from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.expense import Expense, ExpenseParticipant


class ExpenseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_expense(self, expense: Expense, participant_shares: dict[str, int]) -> Expense:
        self.db.add(expense)
        self.db.flush()
        for participant_id, share_cents in participant_shares.items():
            self.db.add(
                ExpenseParticipant(
                    expense_id=expense.id,
                    participant_id=participant_id,
                    share_cents=share_cents,
                )
            )
        self.db.commit()
        return self.get_expense(expense.id) or expense

    def list_group_expenses(self, group_id: str) -> list[Expense]:
        return list(
            self.db.scalars(
                select(Expense)
                .where(Expense.group_id == group_id)
                .options(
                    selectinload(Expense.payer),
                    selectinload(Expense.participants).selectinload(ExpenseParticipant.participant),
                )
                .order_by(Expense.created_at.desc())
            )
        )

    def get_expense(self, expense_id: str) -> Expense | None:
        return self.db.scalar(
            select(Expense)
            .where(Expense.id == expense_id)
            .options(
                selectinload(Expense.payer),
                selectinload(Expense.participants).selectinload(ExpenseParticipant.participant),
            )
        )
