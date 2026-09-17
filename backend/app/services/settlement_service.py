from sqlalchemy.orm import Session

from app.algorithms.debt_settlement import calculate_balances, optimize_settlements
from app.algorithms.money import cents_to_decimal
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.group_repository import GroupRepository
from app.schemas.settlement import GroupSettlementSummary, ParticipantBalance, SettlementRead
from app.services.group_service import GroupService


class SettlementService:
    def __init__(self, db: Session) -> None:
        self.group_service = GroupService(db)
        self.group_repository = GroupRepository(db)
        self.expense_repository = ExpenseRepository(db)

    def summarize_group(self, group_id: str) -> GroupSettlementSummary:
        group = self.group_service.get_group_or_404(group_id)
        participants = self.group_repository.get_participants(group_id)
        participant_names = {participant.id: participant.name for participant in participants}
        expenses = self.expense_repository.list_group_expenses(group_id)
        balance_input = [
            (
                expense.payer_id,
                expense.total_cents,
                {
                    expense_participant.participant_id: expense_participant.share_cents
                    for expense_participant in expense.participants
                },
            )
            for expense in expenses
        ]
        balances = calculate_balances(balance_input)
        for participant in participants:
            balances.setdefault(participant.id, 0)

        settlements = optimize_settlements(balances)
        return GroupSettlementSummary(
            balances=[
                ParticipantBalance(
                    participant_id=participant_id,
                    name=participant_names.get(participant_id, "Unknown"),
                    balance=cents_to_decimal(amount_cents),
                    currency=group.currency,
                )
                for participant_id, amount_cents in sorted(
                    balances.items(),
                    key=lambda item: participant_names.get(item[0], item[0]),
                )
            ],
            settlements=[
                SettlementRead(
                    from_participant_id=payment.from_participant_id,
                    from_name=participant_names.get(payment.from_participant_id, "Unknown"),
                    to_participant_id=payment.to_participant_id,
                    to_name=participant_names.get(payment.to_participant_id, "Unknown"),
                    amount=cents_to_decimal(payment.amount_cents),
                    currency=group.currency,
                )
                for payment in settlements
            ],
        )
