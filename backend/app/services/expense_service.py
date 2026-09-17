from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.algorithms.split_calculator import EqualSplitInput, calculate_equal_split
from app.models.expense import Expense
from app.models.user import AdminUser
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.group_repository import GroupRepository
from app.schemas.expense import ExpenseCreate


class ExpenseService:
    def __init__(self, db: Session) -> None:
        self.group_repository = GroupRepository(db)
        self.expense_repository = ExpenseRepository(db)

    def add_expense(self, group_id: str, payload: ExpenseCreate, admin: AdminUser) -> Expense:
        group = self.group_repository.get_group(group_id)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")
        if group.admin_id != admin.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the group admin can add expenses.",
            )

        participant_ids = set(payload.participant_ids)
        participant_ids.add(payload.payer_id)
        participants = self.group_repository.get_participants(group_id, participant_ids)
        found_ids = {participant.id for participant in participants}
        missing_ids = participant_ids - found_ids
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payer and participants must belong to the group.",
            )

        split = calculate_equal_split(
            EqualSplitInput(
                subtotal=payload.subtotal,
                tax_rate=payload.tax_rate,
                tax_amount=payload.tax_amount,
                tip_rate=payload.tip_rate,
                tip_amount=payload.tip_amount,
                fees=payload.fees,
                discounts=payload.discounts,
                participant_ids=tuple(payload.participant_ids),
            )
        )
        expense = Expense(
            group_id=group_id,
            name=payload.name,
            category=payload.category,
            payer_id=payload.payer_id,
            subtotal_cents=split.subtotal_cents,
            tax_cents=split.tax_cents,
            tip_cents=split.tip_cents,
            fees_cents=split.fees_cents,
            discounts_cents=split.discounts_cents,
            total_cents=split.total_cents,
            currency=group.currency,
            split_method="equal",
            source="manual",
        )
        return self.expense_repository.create_expense(expense, split.shares_by_participant)

    def list_group_expenses(self, group_id: str) -> list[Expense]:
        if self.group_repository.get_group(group_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")
        return self.expense_repository.list_group_expenses(group_id)
