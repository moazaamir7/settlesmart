from dataclasses import dataclass


@dataclass(frozen=True)
class SettlementPayment:
    from_participant_id: str
    to_participant_id: str
    amount_cents: int


def calculate_balances(expenses: list[tuple[str, int, dict[str, int]]]) -> dict[str, int]:
    balances: dict[str, int] = {}

    for payer_id, total_cents, shares_by_participant in expenses:
        balances[payer_id] = balances.get(payer_id, 0) + total_cents
        for participant_id, share_cents in shares_by_participant.items():
            balances[participant_id] = balances.get(participant_id, 0) - share_cents

    return {participant_id: amount for participant_id, amount in balances.items() if amount != 0}


def optimize_settlements(balances: dict[str, int]) -> list[SettlementPayment]:
    debtors = sorted(
        [(participant_id, -amount) for participant_id, amount in balances.items() if amount < 0],
        key=lambda item: item[1],
        reverse=True,
    )
    creditors = sorted(
        [(participant_id, amount) for participant_id, amount in balances.items() if amount > 0],
        key=lambda item: item[1],
        reverse=True,
    )

    payments: list[SettlementPayment] = []
    debtor_index = 0
    creditor_index = 0

    while debtor_index < len(debtors) and creditor_index < len(creditors):
        debtor_id, debt = debtors[debtor_index]
        creditor_id, credit = creditors[creditor_index]
        amount = min(debt, credit)

        if amount > 0:
            payments.append(
                SettlementPayment(
                    from_participant_id=debtor_id,
                    to_participant_id=creditor_id,
                    amount_cents=amount,
                )
            )

        debt -= amount
        credit -= amount

        if debt == 0:
            debtor_index += 1
        else:
            debtors[debtor_index] = (debtor_id, debt)

        if credit == 0:
            creditor_index += 1
        else:
            creditors[creditor_index] = (creditor_id, credit)

    return payments
